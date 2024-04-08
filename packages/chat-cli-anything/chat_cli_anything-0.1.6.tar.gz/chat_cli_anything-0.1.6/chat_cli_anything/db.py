import os
from pathlib import Path
from hashlib import md5
from typing import List, Dict, Any, Sequence, Optional, Tuple
import json
from copy import deepcopy
from chat_cli_anything.util import cache_path, calculate_hash
from chat_cli_anything.config import Config
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from datetime import datetime
from tabulate import tabulate
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine.reflection import Inspector
import logging
from logging import getLogger
from chat_cli_anything.embedding import LocalEmbeddings

logger = getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


DB_PATH = cache_path / 'db' 
if not DB_PATH.exists():
    DB_PATH.mkdir()

engine = create_engine(f"sqlite:///{str(DB_PATH/ 'info.db')}")#, echo=True)

Base = declarative_base()


class DocumentInfoDB(Base):
    """"""
    __tablename__ = 'document_info'
    hash = Column(String, primary_key=True)
    kb_path = Column(String)
    file_path = Column(String)
    modified_time = Column(String)


class DocumentInfo(BaseModel):
    """"""
    hash: str # file hash
    kb_path: str
    file_path: str
    modified_time: str


class DocumentSetDB(Base):
    """"""
    __tablename__ = 'document_set'
    name = Column(String, primary_key=True)
    comment = Column(Integer)
    created_time = Column(String)


class DocumentSet(BaseModel):
    """"""
    name: str # 
    comment: str
    created_time: str


class SetOfDocumentDB(Base):
    """"""
    __tablename__ = 'set_of_document'
    hash = Column(String, ForeignKey('document_info.hash'), primary_key=True)
    name = Column(Integer, ForeignKey('document_set.name'), primary_key=True)


class SetOfDocument(BaseModel):
    """"""
    id: int
    hash: str # document info hash
    name: str # document set name



def load_db(file_path: Path) -> Dict[str, Any]:
    """
    file_path: Path
    """
    if not file_path.exists():
        return {}

    with open(file_path, 'r') as f:
        return json.load(f)


Base.metadata.create_all(engine)


def _generate_name(names: Sequence[str]) -> str:
    """"""
    prefix = ''.join(sorted(names))
    return md5(prefix.encode('utf-8')).hexdigest()


def list_db(name: Optional[str]=None, short: bool=False):
    """
    name: str
    """
    # using tabulate to list db_index_info
    Session = sessionmaker(bind=engine)
    session = Session()

    inspector = Inspector(bind=engine)
    if not inspector.has_table('document_set'):
        return False, 'Empty Table'

    # list all document set
    if name is None:
        names = session.query(DocumentSetDB.name).all()
    else:
        # check whether the name is in document set
        names = session.query(DocumentSetDB).filter(DocumentSetDB.name == name).all()
        if names:
            names = [(name, )]
        else:
            return False, f'No such document set: {name}'
    tables = {}
    _data = []
    for name, *_ in names:
        documents = session.query(SetOfDocumentDB, DocumentInfoDB).filter(SetOfDocumentDB.name == name, SetOfDocumentDB.hash == DocumentInfoDB.hash)
        if short:
            # name, len of docs
            _data.append([name, len(list(documents))])
        else:
            data = []
            for set_doc, doc_info in documents:
                data.append([set_doc.hash, doc_info.file_path, doc_info.modified_time]) # type: ignore
            table = tabulate(
                data, 
                headers=["Hash", "File Path", "Modified Time"],
                tablefmt="simple_outline"
            )
            tables[name] = table
        # files 
    if short:
        tables = tabulate(_data, headers=["Name", "# of Documents"], tablefmt='simple_outline')
    return True, tables


def remove_db(name: str, remove_documents: bool=False):
    """"""
    Session = sessionmaker(bind=engine)
    session = Session()
    inspector = Inspector.from_engine(engine)
    if 'document_set' in inspector.get_table_names():
        if remove_documents:
            session.query(DocumentInfoDB).filter(
                DocumentInfoDB.hash.in_(
                    session.query(SetOfDocumentDB.hash).filter(SetOfDocumentDB.name == name))).delete(synchronize_session=False)
        session.delete(session.query(DocumentSetDB).filter(DocumentSetDB.name == name).first())
    # TODO: opitmize to implement 
    session.commit()
    return True, 'Remove Succeed'


def create_vectorstore(
    docs: List[Document],
    hash_files_processed: Dict[str, str],
    name: str,
    comment: str,
):
    """
    docs:
    files_processed:
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    embedding_model = LocalEmbeddings(Config().get('local_server_port', Config.DEFAULT_PORT))

    inspector = Inspector.from_engine(engine)
    if 'document_set' in inspector.get_table_names():
        # check name not exists
        current_set_with_given_name = session.query(DocumentSetDB).filter(DocumentSetDB.name == name).first()
        print(name)
        if current_set_with_given_name:
            return False, 'Name Already Exists.'

    # from documents
    document_set = DocumentSetDB(name=name,
                               comment=comment,
                               created_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    session.add(document_set)

    for doc, (hash_key, file) in zip(docs, hash_files_processed.items()):

        if not session.query(DocumentInfoDB).filter(DocumentInfoDB.hash == hash_key).first():
            logger.info(f'{hash_key}, {file}')
            faiss_index = FAISS.from_documents(doc, embedding_model)
            kb_path = DB_PATH / (os.path.basename(hash_key).split('.')[0] + '.db')
            faiss_index.save_local(str(kb_path)) # TODO
            
            # update document info table
            modified_time = os.path.getmtime(file)
            modified_datetime = datetime.fromtimestamp(modified_time)
            new_index_info = DocumentInfoDB(hash=hash_key,
                                        kb_path=str(kb_path),
                                        file_path=file,
                                        modified_time=modified_datetime)

            session.add(new_index_info)

        set_doc_exists = 'document_set' in inspector.get_table_names()
        if not (set_doc_exists and session.query(SetOfDocumentDB).filter(SetOfDocumentDB.name == name, SetOfDocumentDB.hash == hash_key).first()):
            session.add(SetOfDocumentDB(hash=hash_key, name=name))

    # update document set table 
    session.commit() 
    return True, 'Successfully created.'


def load_vectorstore(name: str) -> Tuple[bool, Any]:
    """
    name: hash or store name
    """
    embedding_model = LocalEmbeddings(Config().get('local_server_port', Config.DEFAULT_PORT))
    Session = sessionmaker(bind=engine)
    with Session() as session:
        # query from Document Set data base
        res = session.query(DocumentSetDB, SetOfDocumentDB, DocumentInfoDB).filter(DocumentSetDB.name == name, DocumentSetDB.name == SetOfDocumentDB.name, SetOfDocumentDB.hash == DocumentInfoDB.hash).all()
        if not res:
            return False, 'Document set not found.'
        else:
            # convert hash to list in documents
            faiss_index = None
            for _, _, document in res:
                _index = FAISS.load_local(document.kb_path, embedding_model, allow_dangerous_deserialization=True)
                if faiss_index is None:
                    faiss_index = _index
                else:
                    faiss_index.merge_from(_index)
    return True, faiss_index

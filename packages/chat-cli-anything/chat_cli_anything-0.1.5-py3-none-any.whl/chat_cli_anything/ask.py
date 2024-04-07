import click
import socket
import requests
import os
import json
import psutil
from chat_cli_anything.config import Config
from chat_cli_anything.request import build_client, stream_predict, predict
from typing import Dict, Any, Union, Optional, List, TypeVar, Sequence
from copy import deepcopy
from chat_cli_anything.util import parse_markdown_codeblock, cache_path
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
import sys

FAISS = TypeVar("FAISS")


console = Console()


COLORS = ('blue', 'green', 'yellow', 'red', 'magenta', 'cyan')

def go_up_and_back(n: int):
    """Go up lines"""
    if n > 0:
        print("\033[F"*n + '\r', end="")


def get_shell_type():
    """"""
    ppid = os.getppid()
    name = psutil.Process(ppid).name()
    shell_type = name.lower()
    if shell_type == 'python':
        shell_type = 'xonsh'
    return shell_type


def _get_relevant_docs(query: str,
                        db: Optional[FAISS]=None,
                        score_threshold: float=0.7,
                        do_rerank: bool=False,
                        k: int=10) -> Sequence[str]:
    docs_with_score = db.similarity_search_with_score(query, k=10)            # type: ignore
    docs: Sequence[str] = [doc_with_score[0].page_content for doc_with_score  # type: ignore
            in docs_with_score if doc_with_score[1] > score_threshold]        # type: ignore
    if docs and do_rerank:
        from chat_cli_anything.rerank import rerank
        docs = rerank(query, docs)
    return docs


def _build_prompt_from_docs(docs: Sequence[str], show_chunks: bool=False) -> str:
    """"""
    docs_str = ''
    for i, doc in enumerate(docs):
        docs_str += f"{doc}\n\n"
        if show_chunks:
            click.secho(doc, fg=COLORS[i%len(COLORS)])
            click.echo('')

    if docs_str == '':
        docs_str = 'No relevant document found.'
    return docs_str


class Interface:
    """This chat will set chat configuration"""
    _QUIT_STRING = '/quit'
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.config = Config().config
        self.history_file = cache_path / '.history.json'

        if self.history_file.exists():
            with open(self.history_file, 'r') as file:
                self.history = json.load(file)
                self.diag_history = self.history.get('history', [])
                self.last_output = self.history.get('last_output', '')
                self.last_query = self.history.get('last_query', '')
        else:
            self.diag_history = []
            self.last_output = '' 
            self.last_query = '' 

        self.pipeline_input = self._read_from_pipeline_input()
        if 'providers' in self.config and 'active' in self.config:
                self.active_config = self.config['providers'][self.config['active']]
                self.client = build_client(
                    self.active_config['base_url'],
                    self.active_config['api_key'],
                    self.active_config['proxy'],
                )
    
    def _check_providers(self):
        if 'providers' not in self.config:
            click.secho('No provider has been add.', fg='bright_red')
            return False
        return True

    def _check_active_config(self):
        if 'active' not in self.config:
            click.secho('No provider has been set active.', fg='bright_red')
            return False
        return True

    def check_active_config_exists(self):
        """"""
        if self._check_providers() and self._check_active_config():
            return
        sys.exit(1)

    def _read_from_pipeline_input(self):
        import sys
        # check whether there is a pipeline input
        lines: List[str] = []
        if not sys.stdin.isatty():
            # read data from pipeline
            for line in sys.stdin:
                # processing each line
                lines.append(line)
        text = ''.join(lines)
        return text

    def _build_prompt_for_rag(self, text: str):
        prompt = f"""下面是用户的输入，请依据该内容针对用户给出的问题做回答, 
        如果是事实性的问答，且是文档中涉及到，给出文档中内容；
        #如果给出的问题和文档很不相关，则先给出提示 "**问题和文档内容不相关**", 然后另起一行，再给出答案
        ```
        {text}
        ```
"""
        return prompt

    def _build_prompt_for_code(self, text: str):
        prompt = f"""你是一位编程大师，精通各种编程语言，下面是一段代码，
        请完成用户指定的一系列任务，给出回答的时候尽量详细完整
        ```
        {text}
        ```
"""
        return prompt


    def _build_prompt(self, content: str, type: str='', as_system: bool=True):
        """"""
        if type == 'code':
            prompt = self._build_prompt_for_code(content)
        else:
            prompt = self._build_prompt_for_rag(content)

        if as_system:
            self.diag_history.insert(0, {'role': 'system', 'content': prompt})
        else:
            self.diag_history.append({'role': 'user', 'content': prompt})

    def load_file(self, filename: str):
        from chat_cli_anything.loader import SUPPORTED_FILES, load_file
        ext = os.path.splitext(filename)
        if ext[1] and ext[1] in SUPPORTED_FILES: 
            pages = load_file(filename)
            content = ''.join(page.page_content for page in pages)
        else:
            click.secho(click.style('Not supported file extension. ' + f' currrent supported format: {",".join(SUPPORTED_FILES)}', fg='orange') + 'It will be loaded as plain text')
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
        return content

    def chat(self,
             query: str,
             filename: str,
             db: Any,
             not_interactive: bool=False):
        """Start a chat session with the given query."""
        content = None
        if filename:
            if not os.path.exists(filename):
                click.secho(f'Could not find {filename}.', fg='red')
                return
            content = self.load_file(filename)

        elif self.pipeline_input:
            content = self.pipeline_input

        if content or (db is not None):
            self.clear_chat_history()

        if content: 
            self._build_prompt(content)

        interactive = not not_interactive
        if self.active_config is None:
            raise ValueError("No active configuration set. Please switch to a configuration first.")

        while True:
            try:
                if query == self._QUIT_STRING:
                    break

                if db:
                    docs = _get_relevant_docs(query, db)
                    docs_str = _build_prompt_from_docs(docs)
                    # update system prompt
                    self._build_prompt(docs_str, as_system=False)

                # add last query and output into history
                if not_interactive and self.last_output:
                    self.diag_history.append({'role': 'user', 'content': self.last_query})
                    self.diag_history.append({'role': 'assistant', 'content': self.last_output})

                responses = stream_predict(
                    self.client,
                    self.active_config['model'],
                    query=query,
                    history=deepcopy(self.diag_history)
                )

                full_response = ''
                click.secho('Assistant:', fg='blue')

                with Live(Markdown(full_response), refresh_per_second=20) as live:
                    for response in responses:
                        if response.choices[0].delta.content is not None:
                            partial_response = response.choices[0].delta.content
                            full_response += partial_response
                            live.update(Markdown(full_response))
                self.last_output = full_response
                self.diag_history.append({'role': 'user', 'content': query})
                self.diag_history.append({'role': 'assistant', 'content': full_response})

                if interactive:
                    click.secho("\nUser: ", fg='cyan', nl=False)
                    # click.prompt could not throw keyboard interruption
                    query = input("")
                else:
                    break
            except KeyboardInterrupt:
                click.echo('\nExiting...')
                break

        # when in interactive chat mode, output will be cleared
        if interactive:
            self.diag_history = []
        # write history back
        with open(self.history_file, 'w') as f:
            # diag_history + last_output = all diag
            json.dump({'history': self.diag_history[:-2], 'last_query': query, 'last_output': self.last_output},
                       f, ensure_ascii=False, indent=4)

    def show_chat_history(self):
        """Show chat history."""
        for item in self.diag_history:
            click.secho(f"{item['role']}: ".capitalize(), fg='cyan' if item['role'] == 'user' else 'blue', nl=False)
            click.secho(f"{item['content']}")

    def clear_chat_history(self):
        """Clear chat history"""
        self.diag_history.clear()
        # write cleanupped history
        with open(self.history_file, 'w') as f:
            json.dump({'history': self.diag_history, 'last_output': self.last_output}, f, indent=4)

    def ask(self,
            query: str,
            type: str,
            filename: str='',
            db: Optional[FAISS]=None,
            score_threshold: float=0.3,
            do_rerank: bool=False,
            show_chunks: Optional[bool]=False,
            advance:bool=False):
        """Single round query."""

        self.clear_chat_history()

        if filename:
            if not os.path.exists(filename):
                click.secho(f'Could not find {filename}.', fg='red')
                return
            content = self.load_file(filename)
            self._build_prompt(content, type)
        elif db:
            if advance:
                # HyDE
                query = predict(self.client,
                                self.active_config['model'], 
                                f"Please write a passage to answer the question?\n {query}".format(query=query),
                                )
            docs = _get_relevant_docs(query, db, score_threshold, do_rerank)
            docs_str = _build_prompt_from_docs(docs, show_chunks=show_chunks)
            self._build_prompt(docs_str, type)

        elif self.pipeline_input:
            self._build_prompt(self.pipeline_input, type)


        responses = stream_predict(
            self.client,
            self.active_config['model'],
            query,
            history=self.diag_history,
            temperature=0.01 if type == 'code' else 0.5,
        )

        click.secho('Assistant:', fg='blue')
        full_response = ''
        with Live(
            Markdown(full_response),
            refresh_per_second=20,
        ) as live:
            for response in responses:
                if response.choices[0].delta.content is not None:
                    partial_response = response.choices[0].delta.content
                    full_response += partial_response
                    live.update(Markdown(full_response))
        self.last_output = full_response
        with open(self.history_file, 'w') as f:
            json.dump({'history': [], 'last_query': query, 'last_output': self.last_output}, 
                      f, ensure_ascii=False, indent=4)

    def fk(self, query: str):
        """Similar to `thefuck` fix output."""
        # TODO
        ...

    def refactor(self, filename: str, object_name: str, continue_generate: bool):
        """Refactor code."""
        if object_name:
            prompt = f"""重构上面代码中的 `{object_name}` 代码, 你首先应该把目标代码提取出来, 然后再进行重构, 直接输出重构后的代码"""
        else:
            prompt = f"""重构上面的代码"""

        if continue_generate:
            prompt = "请继续输出"
            self.chat(prompt, filename, db=None, not_interactive=True)
        else:
            self.ask(prompt, 'code', filename)

    def explain(self, filename: str, object_name: str, line_by_line: bool, continue_generate: bool):
        """"""
        if object_name:
            prompt = f"""从上面给出代码中, 解释 {object_name} 的函数, 你首先应该把目标代码提取出来, 然后再进行解释"""
            if line_by_line:
                prompt += '逐行给出解释。'
        else:
            prompt = f"""解释上面给出的代码, 对于复杂难懂的地方给出说明"""
            if line_by_line:
                prompt = f"""解释上面给出的代码, 逐行给出解释"""
            else:
                prompt = f"""解释上面给出的代码, 对于复杂难懂的地方给出说明"""

        if continue_generate:
            prompt = "请继续输出"
            self.chat(prompt, filename, db=None, not_interactive=True)
        else:
            self.ask(prompt, 'code', filename)

    def translate(self, filename: str, object_name: str, target_language: str, continue_generate: bool):
        """Translate code from one language to another language"""
        if object_name:
            prompt = f"""把 `{object_name}` 转化为 {target_language} 语言实现, 你首先应该把目标代码提取出来, 然后再进行翻译, 直接输出翻译后的代码"""
        else:
            prompt = f"""把上面给出的代码转化为 {target_language} 语言实现"""

        if continue_generate:
            prompt = "请继续输出"
            self.chat(prompt, filename, db=None, not_interactive=True)
        else:
            self.ask(prompt, 'code', filename)

    def review(self, filename: str, object_name: str, continue_generate: bool):
        """Do code review"""
        instruction = """对需要优化的代码实现，变量命名, 代码分格, 代码注释等给出 comment."""
        if object_name:
            prompt = f"""对 `{object_name}` 实现进行 code review, 你首先应该把目标代码提取出来, 然后再""" + instruction
        else:
            prompt = f"""对上面的代码进行code review, """ + instruction

        if continue_generate:
            prompt = "请继续输出"
            self.chat(prompt, filename, db=None, not_interactive=True)
        else:
            self.ask(prompt, 'code', filename)

    def fix(self, filename: str, object_name: str, continue_generate: bool):
        """Fix given function name"""
        if object_name:
            prompt = f"""修复 `{object_name}` 中可能的错误, 你首先应该把目标代码提取出来, 然后再进行修复, 直接输出修复后的代码"""
        else:
            prompt = f"""修复上面代码其中可能的错误"""

        if continue_generate:
            prompt = "请继续输出"
            self.chat(prompt, filename, db=None, not_interactive=True)
        else:
            self.ask(prompt, 'code', filename)

    def select_code_snippet(self, index: str, count: bool):
        """"""
        blocks = parse_markdown_codeblock(self.last_output)
        if count:
            click.echo(len(blocks))
            return

        if index.isdigit():
            index = int(index)
        else:
            click.secho(f"Invalid index: {index}", fg='red')
            return
        click.echo(blocks[index - 1] if index <= len(blocks) else None)


@click.group()
def cli():
    """Chat CLI."""
    pass

@click.group(name='cc-config')
def config():
    """Manage configurations."""
    pass

@click.group(name='cc-code')
def code():
    """Process code content."""
    pass

@click.group(name='cc-db')
def db():
    """Manage document database."""
    pass

@click.group(name='cc-service')
def service():
    """Manage service"""
    pass


filename = click.argument('filename', required=False, default='')
object_name = click.option('-o', '--object-name', required=False, default='')
continue_generate = click.option('-c', '--continue-generate', is_flag=True)


@config.command()
@click.argument('name', default=None)
@click.argument('base-url', default=None)
@click.option('--model', default='Empty')
@click.option('--api-key', default='Empty', envvar="OPENAI_API_KEY")
@click.option('--proxy')
def add(name: Union[str, None], base_url: Union[str, None],
        api_key: str, model: str, proxy: Optional[str] = None):
    """Add a new configuration."""
    if name is None:
        name = click.prompt('Enter base name')
    if base_url is None:
        base_url = click.prompt('Enter the url')

    config = Config()
    config.add(name, base_url, api_key, model, proxy)
    click.echo(f"Configuration '{name}' added successfully.")


@config.command()
@click.argument('name')
@click.option('-a', '--all', is_flag=True, help='Remove all providers')
def remove(name: str, all: bool):
    """Remove a configuration."""
    config = Config()
    config.remove(name, all)


@config.command()
@click.argument('name', required=False, default='')
@click.option('-s', '--show-api-key', is_flag=True)
def list(name: str, show_api_key: bool):
    """List configurations. The active provider will be marked with '*'."""
    config = Config()
    config.list(name, api_key=show_api_key)  # Set api_key to True or False based on your preference


@config.command()
@click.argument('name', required=True)
def switch(name: str):
    """Switch to a different configuration and save the change."""
    config = Config()
    config.switch(name)


@config.command()
@click.argument('name', required=True)
def ping(name: str):
    """Ping provider."""
    config = Config()
    config.ping(name)


@config.command()
@click.argument('path', required=True)
@click.option('-o', '--override', is_flag=True, help='Whether override existing file.')
def dump(path: str, override: bool):
    """Export current configurations."""
    config = Config()
    config.dump(path, override)

@config.command()
@click.argument('path', required=True)
@click.option('-o', '--override', is_flag=True, help='Whether override original config.')
def load(path: str, override: bool):
    """Import configurations."""
    config = Config()
    config.load(path, override)

@cli.command(name='cc-ask')
@click.argument('query', required=True)
@click.option('-d', '--db', type=str, help='Name of database.')
@click.option('-f', '--filename', type=str, help='Name of file.')
@click.option('-r', '--rerank', is_flag=True, default=False, help='Whether to rerank the results.')
@click.option('-s', '--show-chunks', is_flag=True, help='Whether to show the related chunks retrieved from database.')
@click.option('-a', '--advance', is_flag=True, help='Whether to use advance RAG.')
def ask(query: str, db: Any, filename: str, rerank: bool, show_chunks: bool, advance: bool):
    """Start a chat session with the given query."""
    interface = Interface()
    interface.check_active_config_exists()

    if db is not None:
        from chat_cli_anything.db import load_vectorstore
        _db = db
        status, db = load_vectorstore(db)
        if status:
            check_and_start_service()
        else:
            click.secho(f"The '{_db}' does not exist.", fg='red')
            return
    interface.ask(query, 'chat', filename, db, rerank, show_chunks, advance=advance)


@cli.command(name='cc-chat')
@click.argument('query', required=False, default='')
@click.option('-d', '--db', type=str, help='name of database.')
@click.option('-f', '--filename', type=str, help='Name of file.')
@click.option('-n', '--not-interactive', is_flag=True)
@click.option('-s', '--show-history', is_flag=True)
@click.option('-c', '--clear', is_flag=True)
def chat(query: str,
         filename: str='',
         db: Any='',
         not_interactive: bool=False,
         show_history: bool=False,
         clear: bool=False):
    """Interactive chat. Enter '/quit' to exit"""
    interface = Interface()
    interface.check_active_config_exists()

    if db is not None:
        from chat_cli_anything.db import load_vectorstore
        _db = db
        status, db = load_vectorstore(db)
        if status:
            check_and_start_service()
        else:
            click.secho(f"The {_db} is not exists.", fg='red')
            return
    if show_history:
        interface.show_chat_history()
    elif clear:
        interface.clear_chat_history()
    else:
        print('Chat')
        interface.chat(query, filename, db, not_interactive)


def check_has_context(filename: str):
    if not filename and sys.stdin.isatty():
        click.secho('Please provide a filename or input from pipe.', fg='red')
        sys.exit(1)

@code.command()
@filename
@object_name
@continue_generate
def refactor(filename: str, object_name: str, continue_generate: bool):
    """Refactor code."""
    check_has_context(filename)
    interface = Interface()
    interface.check_active_config_exists()

    interface.refactor(filename, object_name, continue_generate)


@code.command()
@click.argument('language')
@filename
@object_name
@continue_generate
def translate(filename: str, object_name: str, language: str, continue_generate: bool):
    """Translate code from one language to another. Supported languages 
    c++, cpp, c, rust, typescript, javascript, markdown, html.
    """
    check_has_context(filename)
    interface = Interface()
    interface.check_active_config_exists()

    interface.translate(filename, object_name, language, continue_generate)


@code.command()
@filename
@object_name
@continue_generate
def fix(filename: str, object_name: str, continue_generate: bool):
    """Fix code."""
    check_has_context(filename)
    interface = Interface()
    interface.check_active_config_exists()

    interface.fix(filename, object_name, continue_generate)


@code.command()
@filename
@object_name
@continue_generate
def review(filename: str, object_name: str, continue_generate: bool):
    """Review code."""
    check_has_context(filename)
    interface = Interface()
    interface.check_active_config_exists()

    interface.review(filename, object_name, continue_generate)


@code.command()
@filename
@object_name
@click.option('-l', '--line', is_flag=True, help='Line by line.')
@continue_generate
def explain(filename: str, object_name: str, line: bool, continue_generate: bool):
    """Explain code."""
    check_has_context(filename)
    interface = Interface()
    interface.check_active_config_exists()

    interface.explain(filename, object_name, line_by_line=line, continue_generate=continue_generate)


@code.command()
@click.argument('index', required=False, default='')
@click.option('-c', '--count', is_flag=True, help='get number of code snippets')
def select(index: str, count: bool):
    """Select code snippet from last output.

    Argument:
        index: code snippet index
    """
    interface = Interface()

    interface.select_code_snippet(index, count)


@db.command(name='ingest')
@click.argument('files', nargs=-1)
@click.option('-n', '--name', help='The name of the knowledge base.')
@click.option('-m', '--comment', default='', help='Add comment to info')
def ingest(files: str, name: str, comment: str):
    """Read documents and convert it searchable database."""
    from chat_cli_anything.loader import parse_files
    from chat_cli_anything.db import create_vectorstore, _generate_name

    check_and_start_service()

    click.echo('Collecting documents')
    docs, hash_files_processed = [], {}
    for f in files:
        res = parse_files(f)
        if res:
            _docs, _files_processed = res
            docs.extend(_docs)
            hash_files_processed.update(_files_processed)

    if docs and hash_files_processed:
        print(hash_files_processed)
        if not name:
            name = _generate_name(hash_files_processed.keys())
        click.echo(f'{len(docs)} files need to be processed')
        success, status = create_vectorstore(docs, hash_files_processed, name, comment)
        if success:
            click.echo(click.style(f'{len(docs)}', fg='green')
                       +  ' document' + ('s' if len(docs) > 1 else '') + ' ingested into '
                       + click.style(f'{name}', fg='green'))
        else:
            click.secho(f'{status}', fg='red')


@db.command(name='list')
@click.argument('name', type=str, required=False)
@click.option('-s', '--short', is_flag=True, help='List in short format')
def listdb(name: Optional[str]=None, short: bool=False):
    """List all all document database"""
    from chat_cli_anything.db import list_db
    status, res = list_db(name, short)
    if status:
        if short:
            click.echo(res)
        else:
            for name, table in res.items():
                click.echo('db: ' + click.style(name, fg='green'))
                click.echo(table)
    else:
        click.secho(res)

@db.command(name='remove')
@click.argument('name')
@click.option('-d', '--remove-documents', is_flag=True, default=True, help='Remove documents if data')
def removedb(name: str, remove_documents: bool):
    """Remove database in given name."""
    from chat_cli_anything.db import remove_db
    remove_db(name, remove_documents)


@db.command(name='search')
@click.argument('db', type=str)
@click.argument('query', type=str)
@click.option('-k', '--topk', type=int, default=5, help='Number of top results to return.')
def search(db: str, query: str, topk: int):
    """Search in database."""
    from chat_cli_anything.db import load_vectorstore
    _db = db
    status, db = load_vectorstore(db)
    if status:
        check_and_start_service()
    else:
        click.secho(f"The '{_db}' does not exist.", fg='red')
    search_result = db.similarity_search(query, k=topk)
    for i, result in enumerate(search_result):
        click.echo(f"{i+1}. \n {result.page_content}")

def _check_port_is_accessible(port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect(('localhost', port))
            return True
        except ConnectionRefusedError:
            return False

def _is_excepted_service_type(port: int, service_name: str):
    try:
        response = requests.get(f'http://localhost:{port}/ping', timeout=1)
        if response.json()['service_name'] == service_name:
            return True
        return False
    except Exception as ex:
        print(ex)
        return False

def check_and_start_service():
    """
    """
    from chat_cli_anything.service import SERVICE_NAME
    config = Config()
    port = config.config.get('local_service_port', Config.DEFAULT_PORT)


    need_created = True
    if _check_port_is_accessible(port):
        if _is_excepted_service_type(port, SERVICE_NAME):
            click.secho(f'{SERVICE_NAME} is already running background.')
            need_created = False
        else:
            click.secho(f'{port} has been used .')
            port += port

    if need_created:
        # start service in backend with detach from current host
        import shlex
        import subprocess
        cmds = "{} -m chat_cli_anything.service {}".format(sys.executable, port)
        # cmds = "{} -m cli-chat.chat_cli_anything.service {}".format(sys.executable, port)
        cmds = shlex.split(cmds)
        _ = subprocess.Popen(cmds, start_new_session=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        config['local_service_port'] = port
        config.save()
        click.secho(f'{SERVICE_NAME} is running background.')


def show_service():
    from chat_cli_anything.service import SERVICE_NAME
    config = Config()
    port = config.config.get('local_service_port', Config.DEFAULT_PORT)
    if _check_port_is_accessible(port) and _is_excepted_service_type(port, SERVICE_NAME):
        click.secho(f'Service is running on local port ' + click.style(f'{port}', fg='green') + f', check http://localhost:{port}/docs for more inforamtion.')
    else:
        click.echo(f'Service is not running on local machine.')


def stop_service():
    from chat_cli_anything.service import SERVICE_NAME
    config = Config()
    port = config.config.get('local_service_port', Config.DEFAULT_PORT)

    if _check_port_is_accessible(port) and _is_excepted_service_type(port, SERVICE_NAME):
        # get pid of process listened on given port
        import psutil
        import signal

        def get_pid_listening_port(port):
            pid_list = []
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                conns = proc.info.get('connections', []) or []
                for conn in conns:
                    if conn.status == psutil.CONN_LISTEN and conn.laddr.port == port:
                        pid_list.append(proc.info['pid'])
            return pid_list
        
        pid = get_pid_listening_port(port)[0]
        os.kill(pid, signal.SIGTERM)
        click.secho('Process is killed')
    else:
        click.secho('Service is not running.')

@service.command(name='start')
def start():
    check_and_start_service()

@service.command(name='stop')
def stop():
    stop_service()

@service.command(name='status')
def status():
    show_service()

@cli.command(name='cc-info')
def info():
    # list db path
    from chat_cli_anything.db import DB_PATH
    click.secho('db path: {}'.format(DB_PATH))
    # list config path
    click.secho('config path: {}'.format(Config.CONFIG_PATH))

def main():
    cli.add_command(config)
    cli.add_command(code)
    cli.add_command(db)
    cli.add_command(service)
    cli()


if __name__ == '__main__':
    main()

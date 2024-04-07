import re
from typing import List
from pathlib import Path
import hashlib


cache_path = Path.home() / '.cache' / 'cli-chat-anything'
if not cache_path.exists():
    cache_path.mkdir(parents=True)


LANGUAGES = [
    'python', 'javascript', 'typescript', 'cpp',
    'c', 'java', 'php', 'ruby', 'go', 'rust',
    'swift', 'kotlin', 'scala', 'dart', 'rust',
    'lua', 'perl', 'groovy', 'haskell', 'pascal',
    'basic', 'cobol', 'fortran', 'lisp'
]

def parse_markdown_codeblock(text: str) -> List[str]:
    """"""
    matched_str = re.findall('```(.*?)```', text, re.DOTALL)
    code_str: List[str] = []
    for s in matched_str:
        if s.split('\n')[0].lower() in LANGUAGES:
            code_str.append('\n'.join(s.split('\n')[1:]))
    return code_str


def is_accessible(url: str) -> bool:
    """Using click style to make code pretty."""
    pass

def calculate_hash(file_path: str) -> str:
    """Calculate hash of file."""
    with open(file_path, "rb") as file:
        content = file.read()
        return hashlib.md5(content).hexdigest()
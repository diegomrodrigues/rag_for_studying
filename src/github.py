import os
import ast
import logging
from typing import List, Dict, Tuple
from git import Repo
import tempfile
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GitHubRepoCrawlerSplitter(BaseLoader):
    def __init__(self, clone_url: str, branch: str = "main", white_list: List[str] = None, black_list: List[str] = None, 
                 extensions: List[str] = None, chunk_size: int = 1000, chunk_overlap: int = 0):
        self.clone_url = clone_url
        self.branch = branch
        self.white_list = white_list
        self.black_list = black_list
        self.extensions = extensions or []
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.language_map = self._create_language_map()
        logger.info(f"Initialized GitHubRepoCrawlerSplitter with URL: {clone_url}, branch: {branch}")

    def _create_language_map(self) -> Dict[str, Language]:
        language_map = {
            '.py': Language.PYTHON,
            '.js': Language.JS,
            '.java': Language.JAVA,
            '.go': Language.GO,
            '.rb': Language.RUBY,
            '.rs': Language.RUST,
            '.ts': Language.TS,
            '.cpp': Language.CPP,
            '.c': Language.CPP,
            '.cs': Language.CSHARP,
            '.php': Language.PHP,
            '.scala': Language.SCALA,
            '.swift': Language.SWIFT,
            '.md': Language.MARKDOWN,
            '.tex': Language.LATEX,
            '.html': Language.HTML,
            '.sol': Language.SOL,
        }
        logger.debug(f"Created language map with {len(language_map)} entries")
        return language_map

    def load_and_split(self) -> List[Document]:
        logger.info("Starting load_and_split process")
        documents = self.load()
        split_documents = []

        for doc in documents:
            file_extension = os.path.splitext(doc.metadata['file_path'])[1].lower()
            language = self.language_map.get(file_extension, Language.PYTHON)
            logger.debug(f"Processing file: {doc.metadata['file_path']} as {language}")

            if language == Language.PYTHON:
                split_docs = self._split_python_document(doc)
            else:
                splitter = RecursiveCharacterTextSplitter.from_language(
                    language=language,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap
                )
                split_docs = splitter.split_documents([doc])

            split_documents.extend(split_docs)
            logger.debug(f"Split {doc.metadata['file_path']} into {len(split_docs)} chunks")

        logger.info(f"Finished load_and_split process. Total documents: {len(split_documents)}")
        return split_documents

    def _split_python_document(self, doc: Document) -> List[Document]:
        logger.debug(f"Splitting Python document: {doc.metadata['file_path']}")
        try:
            tree = ast.parse(doc.page_content)
        except SyntaxError:
            logger.warning(f"Syntax error in {doc.metadata['file_path']}, falling back to default splitting")
            splitter = RecursiveCharacterTextSplitter.from_language(
                language=Language.PYTHON,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            return splitter.split_documents([doc])

        split_docs = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                class_name, class_docstring = self._get_class_info(node)
                class_content = self._get_node_source(doc.page_content, node)
                class_metadata = {
                    **doc.metadata,
                    "class_name": class_name,
                    "class_docstring": class_docstring
                }
                split_docs.append(Document(page_content=class_content, metadata=class_metadata))
                logger.debug(f"Added class: {class_name}")

                for method in node.body:
                    if isinstance(method, ast.FunctionDef):
                        method_name, method_docstring = self._get_method_info(method)
                        method_content = self._get_node_source(doc.page_content, method)
                        method_metadata = {
                            **class_metadata,
                            "method_name": method_name,
                            "method_docstring": method_docstring
                        }
                        split_docs.append(Document(page_content=method_content, metadata=method_metadata))
                        logger.debug(f"Added method: {method_name}")

            elif isinstance(node, ast.FunctionDef):
                function_name, function_docstring = self._get_method_info(node)
                function_content = self._get_node_source(doc.page_content, node)
                function_metadata = {
                    **doc.metadata,
                    "function_name": function_name,
                    "function_docstring": function_docstring
                }
                split_docs.append(Document(page_content=function_content, metadata=function_metadata))
                logger.debug(f"Added function: {function_name}")

        logger.debug(f"Split Python document into {len(split_docs)} parts")
        return split_docs

    def _get_class_info(self, node: ast.ClassDef) -> Tuple[str, str]:
        return node.name, ast.get_docstring(node) or ""

    def _get_method_info(self, node: ast.FunctionDef) -> Tuple[str, str]:
        return node.name, ast.get_docstring(node) or ""

    def _get_node_source(self, source: str, node: ast.AST) -> str:
        return ast.get_source_segment(source, node) or ""

    def load(self) -> List[Document]:
        logger.info(f"Starting to clone repository: {self.clone_url}")
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Repo.clone_from(self.clone_url, temp_dir, branch=self.branch)
            logger.info(f"Repository cloned to temporary directory: {temp_dir}")
            documents = []

            for root, _, files in os.walk(temp_dir):
                relative_root = os.path.relpath(root, temp_dir)
                
                if not self._is_in_white_list(relative_root) or self._is_in_black_list(relative_root):
                    logger.debug(f"Skipping directory: {relative_root}")
                    continue

                for file in files:
                    if not self._has_valid_extension(file):
                        logger.debug(f"Skipping file with invalid extension: {file}")
                        continue

                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, temp_dir)

                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    metadata = {
                        "source": self._get_source(relative_path),
                        "file_path": relative_path
                    }

                    documents.append(Document(page_content=content, metadata=metadata))
                    logger.debug(f"Added document: {relative_path}")

        logger.info(f"Finished loading documents. Total documents: {len(documents)}")
        return documents

    def _is_in_black_list(self, path: str) -> bool:
        if not self.black_list:
            return False
        return any(path.startswith(folder) for folder in self.black_list)

    def _is_in_white_list(self, path: str) -> bool:
        if not self.white_list:
            return True
        return any(path.startswith(folder) for folder in self.white_list)

    def _has_valid_extension(self, file: str) -> bool:
        if not self.extensions:
            return True
        return any(file.endswith(ext) for ext in self.extensions)

    def _get_source(self, relative_path: str) -> str:
        repo_name = self.clone_url.split('/')[-1].replace('.git', '')
        return f"https://github.com/{self.clone_url.split('/')[-2]}/{repo_name}/blob/{self.branch}/{relative_path}"

# Usage example
crawler_splitter = GitHubRepoCrawlerSplitter(
    clone_url="https://github.com/huggingface/transformers.git",
    branch="main",
    white_list=["src/transformers/pipelines"],
    black_list=["src/transformers/models"],
    extensions=[".md", ".py"],
    chunk_size=1024,
    chunk_overlap=32
)

splits = crawler_splitter.load_and_split()

print(f"Total splits: {len(splits)}")
for i, split in enumerate(splits[:5]):  # Print details of first 5 splits
    print(f"Split {i+1}:")
    print(f"  Content (first 100 chars): {split.page_content[:100]}...")
    print(f"  Metadata: {split.metadata}")
    print()
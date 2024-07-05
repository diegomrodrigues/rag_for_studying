!git clone https://github.com/diegomrodrigues/rag_for_studying.git

import json

with open("/content/rag_for_studying/assets/results/crawler_large-language-models.json") as file:
    crawler_results = json.load(file)

crawler_results

!pip install langchain_experimental langchain_huggingface sentence-transformers pypdf arxiv pymupdf faiss-gpu

from langchain.document_loaders import ArxivLoader
from langchain.document_loaders.merge import MergedDataLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

import asyncio

def extract_arxiv_id_from_url(url):
    last_part = url.split("/")[-1]
    arxiv_id = last_part.replace(".pdf", "")
    return arxiv_id

arxiv_ids = map(extract_arxiv_id_from_url, crawler_results["collected_urls"]["arxiv.org"])
arxiv_ids = list(arxiv_ids)
print(f"Found {len(arxiv_ids)} Arxiv IDs")

docs_to_merge = []

for arxiv_id in arxiv_ids:
    loader = ArxivLoader(query=arxiv_id)
    docs_to_merge.append(loader)

all_loaders = MergedDataLoader(loaders=docs_to_merge)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=32)

all_chunks = all_loaders.load_and_split(text_splitter)
print(f"Found {len(all_chunks)} chunks")

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    show_progress=True,
    model_kwargs={'device': 'cuda'}
)

vectorstore = FAISS.from_documents(all_chunks, embeddings)

vectorstore.save_local("/content/rag_for_studying/assets/retrievers/large_language_models")


import json
from langchain_community.document_loaders import ArxivLoader
from langchain_community.document_loaders.merge import MergedDataLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from typing import Iterator

class CustomArxivLoader(ArxivLoader):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def lazy_load(self) -> Iterator[Document]:
        documents = super().lazy_load()

        def update_metadata(documents):
            for document in documents:
                summary = document.metadata["Summary"]

                del document.metadata["Summary"]

                yield Document(
                    page_content=summary,
                    metadata={
                        **document.metadata,
                        "Source": f"https://arxiv.org/pdf/{self.query}.pdf"
                    }
                )
        
        return update_metadata(documents)

retriever = "large-language-models"

with open(f"./assets/results/crawler_{retriever}.json") as file:
    results = json.load(file)

arxiv_urls = results["collected_urls"]["arxiv.org"]
arxiv_ids = map(lambda url: url.split("/")[-1].strip(".pdf"), arxiv_urls)

all_loaders = [ArxivLoader(query=arxiv_id) for arxiv_id in arxiv_ids]

merged_loader = MergedDataLoader(loaders=all_loaders)
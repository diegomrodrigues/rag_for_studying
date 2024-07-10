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
                yield Document(
                    page_content=document.metadata["Summary"],
                    metadata={
                        **document.metadata,
                        "Source": f"https://arxiv.org/pdf/{self.query}.pdf",
                        "Content": document.page_content
                    }
                )
        
        return update_metadata(documents)

if __name__ == "__main__":
    retriever = "llm-rl-human-feedback"

    with open(f"./assets/results/crawler_{retriever}.json") as file:
        results = json.load(file)
    
    arxiv_urls = results["collected_urls"]["arxiv.org"]
    arxiv_ids = map(lambda url: url.split("/")[-1].strip(".pdf"), arxiv_urls)
    
    all_loaders = [CustomArxivLoader(query=arxiv_id) for arxiv_id in arxiv_ids]

    merged_loader = MergedDataLoader(loaders=all_loaders)

    documents = merged_loader.load()

    print(f"Found {len(documents)} documents")

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        show_progress=True,
        model_kwargs={'device': 'cpu'}
    )

    vectorstore = FAISS.from_documents(documents, embeddings)

    vectorstore.save_local(f"./assets/retrievers/{retriever}")

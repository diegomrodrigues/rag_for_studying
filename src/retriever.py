from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    show_progress=True,
    model_kwargs={'device': 'cpu'}
)

vectorstore = FAISS.load_local(
    './assets/retrievers/large_language_models', 
    embeddings, 
    allow_dangerous_deserialization=True
)

def retrieve(query, retriever):
    results = retriever.invoke(query)

    documents = []

    for idx, doc in enumerate(results):
        document = (
            f"<Document index={idx+1} title={doc.metadata['Title']}>" +
                "<Sumary>" +
                    doc.metadata['Summary'] +
                "</Sumary>" +
                "<Content>" +
                    doc.page_content +
                "</Content>" +
            "</Document>"
        )

        documents.append(document)

    return documents

def create_prompt_for_summary(query):
    with open("./assets/templates/Template para RAG Artigos.md", "r") as f:
        template = f.read()

    retriever = vectorstore.as_retriever(search_kwargs={"k": 15})

    documents = retrieve(query, retriever)

    context = "\n".join(documents)
    context = f"""<context>
    {context}
    </context>"""

    template = template.replace("<context></context>", context)
    template = (
        template + "\n\n" +
        "X = " + query
    )

    return template

import gradio as gr

def chat_interface(query):
    return create_prompt_for_summary(query)

demo = gr.Interface(
    fn=chat_interface,
    inputs=gr.Textbox(lines=2, placeholder="Enter your question here..."),
    outputs=gr.Textbox(lines=10, show_copy_button=True),
    title="Simple RAG Template for Generation",
    description="Generates a prompt for late being used in Gemini with long context window",
    theme="default"
)

demo.launch(share=True)
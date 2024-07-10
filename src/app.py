import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import gradio as gr

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    show_progress=True,
    model_kwargs={'device': 'cpu'}
)

def load_vectorstore(name):
    return FAISS.load_local(
        f"./assets/retrievers/{name}", 
        embeddings, 
        allow_dangerous_deserialization=True
    )

def format_document(idx, document):
    document_str = ""

    for key, value in document.metadata.items():
        document_str += f"<{key}>"
        document_str += value
        document_str += f"</{key}>"
    
    return (
        f"<Document index={idx}>" +
        document_str +
        "</Document>"
    )

def retrieve(query, retriever):
    results = retriever.invoke(query)

    documents = []

    for idx, doc in enumerate(results):
        document = format_document(idx+1, doc)
        documents.append(document)

    return documents

def create_prompt_for_summary(query, retriever_name, num_results):
    with open("./assets/templates/Template para RAG Artigos.md", "r") as f:
        template = f.read()

    vectorstore = load_vectorstore(retriever_name)
    retriever = vectorstore.as_retriever(search_kwargs={"k": num_results})

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

def chat_interface(query, retriever_path, num_results):
    return create_prompt_for_summary(query, retriever_path, num_results)

def call_gemini_model(prompt):
    return prompt

# Get list of retriever paths
retriever_names = [f for f in os.listdir('./assets/retrievers') if os.path.isdir(os.path.join('./assets/retrievers', f))]


with gr.Blocks(theme="default") as demo:
    gr.Markdown("# Simple RAG Template for Generation")
    gr.Markdown("Generates a prompt for later use in Gemini with long context window")
    
    with gr.Row():
        with gr.Column():
            question = gr.Textbox(lines=2, label="Question", placeholder="Enter your question here...")
            retriever = gr.Dropdown(choices=retriever_names, label="Select Retriever")
            num_results = gr.Number(label="Num. Results", value=4)
        
        with gr.Column():
            raw_output = gr.Textbox(lines=10, show_copy_button=True)
    
    submit_btn = gr.Button("Generate")

    with gr.Row():
        model_output = gr.Markdown("Gemini output...")

    submit_btn.click(
        fn=chat_interface,
        inputs=[question, retriever, num_results],
        outputs=raw_output
    ).then(
        fn=call_gemini_model,
        inputs=raw_output,
        outputs=model_output
    )

demo.launch(share=False)
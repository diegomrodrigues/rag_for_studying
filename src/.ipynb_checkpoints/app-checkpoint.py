import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import google.generativeai as genai
import gradio as gr

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    show_progress=True,
    model_kwargs={'device': 'cpu'}
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

generation_config = {
  "temperature": 0.7,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192 * 4,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config
)

def get_template_markdown(name):
    with open(f"./assets/templates/{name}.md", "r") as f:
        template = f.read()
    
    return template

TEMPLATE_HEADER = get_template_markdown("Header")
TEMPLATE_INTRO = get_template_markdown("Intro")
TEMPLATE_CONTENT = get_template_markdown("Content")

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

def construct_full_template(documents, query):
    context = "\n".join(documents)
    context = f"""<context>
    {context}
    </context>"""

    template = TEMPLATE_HEADER
    template = template.replace("<template></template>", TEMPLATE_INTRO + "\n" + TEMPLATE_CONTENT)

    template = context + "\n" + template
    template = template + "\n" + f"X = {query}"

    return template    

def create_prompt_for_summary(query, retriever_name, num_results):
    vectorstore = load_vectorstore(retriever_name)
    retriever = vectorstore.as_retriever(search_kwargs={"k": num_results})

    documents = retrieve(query, retriever)

    template = construct_full_template(documents, query)

    return template

def chat_interface(query, retriever_path, num_results):
    return create_prompt_for_summary(query, retriever_path, num_results)

def call_gemini_model(prompt):

    chat_session = model.start_chat(history=[])

    response = chat_session.send_message(prompt)

    return response.text

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

demo.launch(share=False, enable_queue=True)
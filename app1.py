from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.agents.agent_toolkits import (
    create_vectorstore_agent,
    VectorStoreToolkit,
    VectorStoreInfo
)

app = Flask(__name__)

# Set API key for OpenAI Service
os.environ['OPENAI_API_KEY'] = 'your_openai_api_key'

# Create an instance of OpenAI LLM
llm = OpenAI(temperature=0.1, verbose=True)
embeddings = OpenAIEmbeddings()

# Define the directory where uploaded files will be stored
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])  # Define a route to handle file uploads
def upload_file():
    # Check if the POST request contains a file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    # Check if the user did not select a file
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Check if the file has an allowed extension
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file extension'})

    # Generate a secure filename and save the file to the upload folder
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    return jsonify({'message': 'File uploaded successfully', 'file_path': file_path})

@app.route('/ask', methods=['POST'])  # Define a route to handle user questions
def ask_question():
    # Process the uploaded file with Langchain (similar to your previous code)
    file_path = request.form.get('file_path')  # Get the file path from the request

    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    store = Chroma.from_documents(pages, embeddings, collection_name='uploaded_report')

    vectorstore_info = VectorStoreInfo(
        name="uploaded_report",
        description="User-uploaded annual report as a PDF",
        vectorstore=store
    )

    toolkit = VectorStoreToolkit(vectorstore_info=vectorstore_info)
    agent_executor = create_vectorstore_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True
    )

    # Process the prompt (you can add error handling if needed)
    prompt = request.form.get('prompt')
    response = agent_executor.run(prompt)

    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, session
import os
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
os.environ['OPENAI_API_KEY'] = 'yourkey'
app.secret_key='yourkey'

# Create an instance of OpenAI LLM
llm = OpenAI(temperature=0.1, verbose=True)
embeddings = OpenAIEmbeddings()


UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the UPLOAD_FOLDER exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the POST request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Check if the file has an allowed extension (e.g., PDF)
    allowed_extensions = {'pdf'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': 'Invalid file type. Allowed types: pdf'}), 400

    # Save the file to the UPLOAD_FOLDER
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    return jsonify({'message': 'File uploaded successfully'}), 200
        

@app.route('/ask', methods=['POST'])
def ask_question():
        # Get the file path from the session
    file_path = session.get('file_path')

    if file_path is None:
        return jsonify({'response': 'Please upload a file first.'})
    # Process the uploaded file with Langchain (similar to your previous code)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], request.form.get('file_name'))
    print("File Path:", file_path)

    # Get the file path from the request
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

    # Return the response as JSON
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)

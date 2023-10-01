import os
from flask import Flask, render_template, request, session, jsonify
import yfinance as yf
from newsapi import NewsApiClient
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.agents.agent_toolkits import (
    create_vectorstore_agent,
    VectorStoreToolkit,
    VectorStoreInfo,
)

app = Flask(__name__)

# Set API key for OpenAI Service

app.secret_key = ""
os.environ["OPENAI_API_KEY"] = app.secret_key

# Create an instance of OpenAI LLM
llm = OpenAI(temperature=0.1, verbose=True)
embeddings = OpenAIEmbeddings()


# Define the directory where uploaded files will be stored
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def main():
    return render_template("index.html")


####################################### NEWS API ####################################################
newsapi = NewsApiClient(api_key="")


@app.route("/news", methods=["POST"])
def render_news():
    return render_template("news.html")


@app.route("/get-news", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_query = request.form["query"]

        # Get top headlines based on user query
        top_headlines = newsapi.get_top_headlines(
            q=user_query, language="en", country="us"
        )
        top_headlines = top_headlines["articles"][:10]

        # Get all articles based on user query
        all_articles = newsapi.get_everything(
            q=user_query, language="en", sort_by="relevancy"
        )

        all_articles = all_articles["articles"][:10]

        return render_template(
            "news.html",
            user_query=user_query,
            top_headlines=top_headlines,
            all_articles=all_articles,
        )

    return render_template("news.html")


######################################## GPT BANKER API ###############################################


@app.route("/gpt-banker", methods=["POST"])
def render_gpt_banker():
    return render_template("gpt_banker.html")


@app.route("/upload", methods=["POST"])
def success():
    if request.method == "POST":
        f = request.files["file"]
        if f:
            # Ensure the 'uploads' directory exists
            if not os.path.exists(app.config["UPLOAD_FOLDER"]):
                os.makedirs(app.config["UPLOAD_FOLDER"])

            # Save the uploaded file to the 'uploads' directory
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], f.filename)
            f.save(file_path)
            print("File Uploaded")

            # Store the file path in the session
            session["file_path"] = file_path

            return render_template("gpt_banker.html", name=f.filename)


@app.route("/ask", methods=["POST"])
def ask_question():
    # Get the file path from the session
    file_path = session.get("file_path")

    if file_path is None:
        return jsonify({"response": "Please upload a file first."})
    # Process the uploaded file with Langchain (similar to your previous code)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], request.form.get("file_name"))
    print("File Path:", file_path)

    # Get the file path from the request
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    store = Chroma.from_documents(pages, embeddings, collection_name="uploaded_report")

    vectorstore_info = VectorStoreInfo(
        name="uploaded_report",
        description="User-uploaded annual report as a PDF",
        vectorstore=store,
    )

    toolkit = VectorStoreToolkit(vectorstore_info=vectorstore_info)
    agent_executor = create_vectorstore_agent(llm=llm, toolkit=toolkit, verbose=True)

    # Process the prompt (you can add error handling if needed)
    prompt = request.form.get("prompt")
    response = agent_executor.run(prompt)

    # Return the response as JSON
    return jsonify({"response": response})


################################################### FINANCE CONVERT API ##########################################################


@app.route("/finance", methods=["POST"])
def render_finance():
    return render_template("finance.html")


@app.route("/quote")
def display_quote():
    symbol = request.args.get("symbol", default="AAPL")

    quote = yf.Ticker(symbol)

    return quote.info


@app.route("/history")
def display_history():
    symbol = request.args.get("symbol", default="AAPL")
    period = request.args.get("period", default="1y")
    interval = request.args.get("interval", default="1mo")
    quote = yf.Ticker(symbol)
    hist = quote.history(period=period, interval=interval)
    data = hist.to_json()
    return data


if __name__ == "__main__":
    app.run(debug=True)

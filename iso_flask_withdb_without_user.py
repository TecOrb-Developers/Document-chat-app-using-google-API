import os
import PyPDF2
from flask import Flask, render_template, request
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import google.generativeai as genai
import logging
import warnings
import mysql.connector

warnings.filterwarnings("ignore")

load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

def get_text_from_pdf(pdf_file):
    text = ""
    try:
        with open(pdf_file, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
    except FileNotFoundError:
        logging.error(f"File '{pdf_file}' not found.")
    except Exception as e:
        logging.error(f"An error occurred while reading the file: {e}")
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    if not embeddings:
        logging.error("Failed to generate embeddings.")
        return None
    
    if not text_chunks:
        logging.error("No text chunks provided.")
        return None
    
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    if not vector_store:
        logging.error("Failed to create vector store.")
        return None
    
    vector_store.save_local("faiss_index")
    return vector_store

def answer():
    prompt_template = """
    You are an AI assistant that provides helpful answers to user queries.\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer: 
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain

def user_input(user_question, vector_store):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    search = vector_store.similarity_search(user_question)

    ans = answer()

    response = ans(
        {"input_documents": search, "question": user_question}
        , return_only_outputs=True)

    if response:
        answer_text = response['output_text']
        logging.info(f"Question: {user_question}, \n\n  Answer: {answer_text}")
    else:
        answer_text = "Not found in document."
        logging.warning(f"Question: {user_question}, Answer: {answer_text}")

    return clean_text(answer_text)

def clean_text(output_text):
    cleaned_text = output_text.strip()
    cleaned_text = '\n'.join(line for line in cleaned_text.splitlines() if line.strip())
    return cleaned_text

def save_to_database(question, answer):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="abkmysql",
            database="chat"
        )
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS qa (question TEXT, answer TEXT)")
        cursor.execute("INSERT INTO qa (question, answer) VALUES (%s, %s)", (question, answer))
        conn.commit()
    except mysql.connector.Error as error:
        logging.error(f"Failed to insert into MySQL table: {error}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def display_stored_chats():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="abkmysql",
            database="chat"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM qa")
        stored_chats = cursor.fetchall()
        return stored_chats
    except mysql.connector.Error as error:
        logging.error(f"Failed to retrieve data from MySQL table: {error}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_question = request.form['question']
        answer_text = user_input(user_question, vector_store)
        save_to_database(user_question, answer_text)  # Save question and answer to database
        stored_chats = display_stored_chats()  # Display stored chats in the terminal
        return render_template('chat.html', chat_history=stored_chats, question=user_question, answer=answer_text)
    else:
        stored_chats = display_stored_chats()
        return render_template('chat.html', chat_history=stored_chats)

def main():
    logging.info("Loading PDF file...")
    
    file = "docs/ISO+13485-2016.pdf"
    logging.info(f"Loaded file: {file}")
    
    text = get_text_from_pdf(file)
    logging.info("PDF file processed. Extracting text...")
    
    chunks = get_text_chunks(text)
    logging.info("Text extracted. Splitting text into chunks...")
    
    global vector_store
    vector_store = get_vector_store(chunks)
    logging.info("Text chunks processed. Vector store created.")

    # Start the Flask application
    app.run(debug=True, port=9000)

if __name__ == "__main__":
    main()










# @app.route('/', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         phone_number = request.form['phone_number']
#         password = request.form['password']
#         if validate_login(phone_number, password):
#             session['phone_number'] = phone_number  # Set phone_number in session
#             return redirect(url_for('dashboard'))
#         else:
#             return render_template('login.html', error='Invalid phone number or password.')
#     return render_template('login.html')



# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         name = request.form['name']
#         phone_number = request.form['phone_number']
#         password = request.form['password']
#         register_user(name, phone_number, password)
#         print(f"New user with phone number '{phone_number}' signed up successfully.")
#         return redirect(url_for('login'))
#     return render_template('signup.html')

# @app.route('/dashboard',methods=['GET', 'POST'])
# def dashboard():
#     if 'phone_number' in session:
#         phone_number = session['phone_number']
#         db_name = f"user_{phone_number}"
#         connection = pymysql.connect(**db_config)
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT name FROM users WHERE phone_number = %s", (phone_number,))
#             user_info = cursor.fetchone()
#         connection.close()
#         if user_info:
#             name = user_info[0]
#             # return f"Welcome, {name}! This is your dashboard."
#             return render_template('index.html', name=name)
#     return redirect(url_for('login'))

# @app.route('/chat', methods=['GET', 'POST'])
# def chat():
#     if request.method == 'POST':  # Check if the request method is POST
#         if 'phone_number' in session:
#             phone_number = session['phone_number']
#             user_question = request.form.get('question')  # Get the question from the form
#             if user_question:
#                 # Assuming you get the answer from somewhere, for example, using your answer_question_from_pdf function
#                 answer = answer_question_from_pdf('pdf', user_question)  # You need to implement this function
#                 save_to_database(phone_number, user_question, answer)
#                 stored_chats = display_stored_chats()
#                 return render_template('dashboard.html', chat_history=stored_chats, question=user_question, answer=answer)
#             else:
#                 # If 'question' key is missing in the form data
#                 return render_template('chat.html', error='Question is missing in the form data.')
#         else:
#             stored_chats = display_stored_chats()
#             return render_template('dashboard.html', chat_history=stored_chats)
#     else:
#         # Handle GET requests for the /chat route
#         # Render the chat.html template for GET requests
#         return render_template('chat.html')
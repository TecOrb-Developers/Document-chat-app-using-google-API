from flask import Flask, render_template, request, redirect, url_for, session
from iso_echqry_insrt_with_user_id_usr_name import signup_page_fun,login_page_fun
from iso_qa_export import answer_question_from_pdf
import pymysql.cursors


app = Flask(__name__)
app.secret_key = b'\xfd\x9dd\xfbN\xfa\xca\xd7\x0f\x84\x8f~\xc6yd\t\xe3\x1c \x8b\x8c;\xbc\xda'


# Database connection
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='abkmysql',
                             database='chat',
                             cursorclass=pymysql.cursors.DictCursor)



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form['action'] == 'signup':
            return redirect(url_for('signup'))
        elif request.form['action'] == 'login':
            return redirect(url_for('login'))
    return render_template('index_iso_echqry.html')


from flask import redirect, url_for

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            return "Username and password cannot be empty. Please try again."
        else:
            message = signup_page_fun(username, password)  # Assuming signup function returns a message
            print("Signup message:", message)  # Debugging message
            if message == "Signup successful":
                return redirect(url_for('login'))
            return message

    return render_template('signup_iso_echqry.html')



def get_questions_and_answers(user_id):
    try:
        with connection.cursor() as cursor:
            # Retrieve questions and answers for the given user ID
            cursor.execute("SELECT question, answer FROM users WHERE user_id=%s", (user_id,))
            questions_and_answers = cursor.fetchall()
            return questions_and_answers
    except Exception as e:
        return []
    
def add_question_and_answer(user_id, question, answer):
    try:
        with connection.cursor() as cursor:
            # Fetch user data based on user_id
            cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
            existing_data = cursor.fetchone()

            if existing_data:
                # Check if the user already has a question and answer
                if existing_data['question'] is None and existing_data['answer'] is None:
                    # If not, update the existing row
                    cursor.execute("UPDATE users SET question=%s, answer=%s WHERE user_id=%s", (question, answer, user_id))
                    print("Question and answer updated successfully!")
                else:
                    # If yes, insert a new row
                    cursor.execute("""
                        INSERT INTO users (user_id,username,password, question, answer)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (existing_data['user_id'], existing_data['username'], existing_data['password'], question, answer))
                    print("New row inserted with question and answer.")
                    
                connection.commit()
                return True
            else:
                print("User with ID {} not found.".format(user_id))
                return False
    except Exception as e:
        print("An error occurred:", str(e))
        return False



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_id, username = login_page_fun(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('dashboard'))  # Redirect to dashboard route upon successful login
        else:
            return "Login failed. Invalid username or password."

    return render_template('login_iso_echqry.html')

# @app.route('/ask', methods=['POST'])
# def ask():
    if 'user_id' in session:
        user_id = session['user_id']
        if request.method == 'POST':
            new_question = request.form.get('new_question')
            file = "/Users/macbook/Desktop/multiusrdb/docs/ISO+13485-2016.pdf"
            new_answer = answer_question_from_pdf(file, new_question)
            if new_question and new_answer:  # Ensure both question and answer are provided

                if add_question_and_answer(user_id, new_question, new_answer):
                    return redirect(url_for('dashboard'))
                else:
                    return "Error: Failed to add question and answer to the database."
            else:
                return "Error: Please provide both a question and an answer."
    else:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

# # @app.route('/dashboard')
# # def dashboard():
# #     if 'user_id' in session:
# #         return "Welcome to the dashboard, " + session['username'] + "!"
# #     else:
# #         return redirect(url_for('login'))

# # @app.route('/dashboard')
# # def dashboard():
#     if 'user_id' in session:
#         user_id = session['user_id']
#         username = session['username']
        
#         questions_and_answers = get_questions_and_answers(user_id)
#         return render_template('dashboard.html', username=username, questions_and_answers=questions_and_answers)
#     else:
#         return redirect(url_for('login_route')) 
    
    
#  with stop exceptions:
@app.route('/ask', methods=['POST'])
def ask():
    if 'user_id' in session:
        user_id = session['user_id']
        if request.method == 'POST':
            new_question = request.form.get('new_question')
            file = "/Users/macbook/Desktop/multiusrdb/docs/ISO+13485-2016.pdf"
            
            try:
                new_answer = answer_question_from_pdf(file, new_question)
                
                if new_question and new_answer:  # Ensure both question and answer are provided
                    if add_question_and_answer(user_id, new_question, new_answer):
                        return redirect(url_for('dashboard'))
                    else:
                        return "Error: Failed to add question and answer to the database."
                else:
                    return "Error: Please provide both a question and an answer."
            
            except Exception as e:
                # Print the exception and insert "Oops" into the answer variable
                print("An exception occurred:", e)
                new_answer = "Oops! An error occurred while processing your request."
                # Assuming 'add_question_and_answer()' is still called even after an exception
                add_question_and_answer(user_id, new_question, new_answer)
                return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in




@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        username = session['username']
        
        if request.method == 'POST':
            new_question = request.form['new_question']
            new_answer = request.form['new_answer']
            if add_question_and_answer(user_id, new_question, new_answer):
                # If adding question and answer is successful, redirect to dashboard to display updated list
                return redirect(url_for('dashboard'))

        questions_and_answers = get_questions_and_answers(user_id)
        return render_template('dashboard.html', username=username, questions_and_answers=questions_and_answers)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True,port=3000)
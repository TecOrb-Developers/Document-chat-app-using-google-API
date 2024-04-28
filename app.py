from flask import Flask, render_template, request, redirect, url_for, session
from terminal_based_eachusrhavetbl import validate_login,register_user,answer_question_from_pdf,save_to_database,print_stored_chat
import pymysql

app = Flask(__name__)
app.secret_key = b'\xfd\x9dd\xfbN\xfa\xca\xd7\x0f\x84\x8f~\xc6yd\t\xe3\x1c \x8b\x8c;\xbc\xda'

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'abkmysql',
    'database': 'all_users'  # Parent database name to contain all user databases
}

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle signup form submission
        name = request.form['name']
        phone_number = request.form['phone_number']
        password = request.form['password']
        
        # Call register_user function passing name, phone_number, password
        register_user(name, phone_number, password)
        
        # Redirect to login page after successful signup
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login form submission
        phone_number = request.form['phone_number']
        password = request.form['password']
        
        # Call validate_login function passing phone_number, password
        if validate_login(phone_number, password):
            # If login successful, set session and redirect to chat page
            session['phone_number'] = phone_number
            return redirect(url_for('chat'))
        else:
            error = "Invalid phone number or password. Please try again."
            return render_template('login.html', error=error)
    return render_template('login.html')


# @app.route('/chat', methods=['GET', 'POST'])
# def chat():
#     if 'phone_number' in session:
#         phone_number = session['phone_number']
#         if request.method == 'POST':
#             # Handle chat form submission
#             user_question = request.form['question']
#             # Call function to get answer and save to database
#             answer = answer_question_from_pdf("/Users/macbook/Desktop/multiusrdb/docs/ISO+13485-2016.pdf", user_question)
#             save_to_database(phone_number, user_question, answer)
#             # Redirect to chat page after saving
#             return redirect(url_for('chat'))
#         else:
#             # Fetch stored chat from the database using your function
#             stored_chat = print_stored_chat(phone_number)  # Replace with your function to fetch stored chat
#             return render_template('chat.html', stored_chat=stored_chat)
#     else:
#         return redirect(url_for('login'))

conn = pymysql.connect(**db_config)

@app.route('/')
def index():
    if 'phone_number' in session:
        phone_number = session['phone_number']
        cursor = conn.cursor(dictionary=True)
        user_table_name = f"user_{phone_number}"
        query = 'SELECT question, answer FROM user WHERE user_table_name = %s'
        cursor.execute(query, (phone_number,))
        data = cursor.fetchall()
        cursor.close()
        return render_template('index.html', data=data)
    else:
        return 'You are not logged in.'
    
    

@app.route('/logout')
def logout():
    session.pop('phone_number', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)

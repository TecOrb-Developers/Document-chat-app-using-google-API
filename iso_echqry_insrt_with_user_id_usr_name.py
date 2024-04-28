import hashlib
import time
import pymysql.cursors
from iso_qa_export import answer_question_from_pdf

# Function to print table in a tabular format
def print_table(data):
    if not data:
        print("No records found.")
        return

    # Define column headers
    headers = data[0].keys()

    # Print headers
    print("\t".join(headers))

    # Print rows
    for row in data:
        print("\t".join(str(row[header]) for header in headers))

# Connect to the MySQL database (or create it if it doesn't exist)
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='abkmysql',
                             database='chat',
                             cursorclass=pymysql.cursors.DictCursor)

# Create users table if not exists
with connection.cursor() as cursor:
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id VARCHAR(10),
                        username VARCHAR(255),
                        password VARCHAR(255),
                        question TEXT,
                        answer TEXT
                    )''')
    connection.commit()

user_id_counter = 0  # Unique counter for generating user IDs

def generate_user_id(username, password):
    global user_id_counter  # Access the global user_id_counter variable

    combined = username + password + str(int(time.time())) + str(user_id_counter)
    # Hash the combined string to generate a unique user ID
    user_id = int(hashlib.sha256(combined.encode()).hexdigest(), 16) % (10 ** 10)  # Limit to 10 digits
    user_id_counter += 1  # Increment the counter for the next user
    return user_id

def signup():
    username = input("Enter username: ")
    password = input("Enter password: ")

    if not username or not password:
        print("Username and password cannot be empty. Please try again.")
        return

    try:
        # Check if the username already exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                # If the username exists, check if the password matches
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if existing_user['password'] != hashed_password:
                    # If the passwords don't match, create a new user
                    user_id = generate_user_id(username, password)
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()
                    cursor.execute("INSERT INTO users (user_id, username, password, question, answer) VALUES (%s, %s, %s, %s, %s)",
                                   (user_id, username, hashed_password, None, None))
                    connection.commit()
                    print("New user created successfully!")
                    return
                else:
                    print("Username already exists. Please choose a different username.")
                    return

            # Generate user ID
            user_id = generate_user_id(username, password)

            # Hash the password before storing it
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Insert user data into the database
            cursor.execute("INSERT INTO users (user_id, username, password, question, answer) VALUES (%s, %s, %s, %s, %s)",
                          (user_id, username, hashed_password, None, None))
            connection.commit()
            print("Signup successful!")
    except Exception as e:
        print("An error occurred during signup:", str(e))


def signup_page_fun(username, password):
    if not username or not password:
        return "Username and password cannot be empty. Please try again."

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if existing_user['password'] != hashed_password:
                    # If the passwords don't match, create a new user
                    user_id = generate_user_id(username, password)
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()
                    cursor.execute("INSERT INTO users (user_id, username, password, question, answer) VALUES (%s, %s, %s, %s, %s)",
                                   (user_id, username, hashed_password, None, None))
                    connection.commit()
                    return "New user created successfully!"
                else:
                    return "Username already exists. Please choose a different username."
            
            # Generate user ID
            user_id = generate_user_id(username, password)
            
            # Hash the password before storing it
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Insert user data into the database
            cursor.execute("INSERT INTO users (user_id, username, password, question, answer) VALUES (%s, %s, %s, %s, %s)",
                           (user_id, username, hashed_password, None, None))
            connection.commit()
            return "Signup successful!"
    except Exception as e:
        return "An error occurred during signup: " + str(e)


def login():
    username = input("Enter username: ")
    password = input("Enter password: ")

    # Hash the password for comparison
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    try:
        with connection.cursor() as cursor:
            # Check if the username and hashed password match what's in the database
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, hashed_password))
            user = cursor.fetchone()
            if user:
                print("Login successful!")
                return user['user_id'], user['username'], user['password']  # Return user ID, username, and password
            else:
                print("Login failed. Invalid username or password.")
                return None, None, None
    except Exception as e:
        print("An error occurred:", str(e))
        
        
def login_page_fun(username, password):
    # Hash the password for comparison
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    try:
        with connection.cursor() as cursor:
            # Check if the username and hashed password match what's in the database
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, hashed_password))
            user = cursor.fetchone()
            if user:
                return user['user_id'], user['username']
            else:
                return None, None
    except Exception as e:
        return None, None



def update_question_and_answer(user_id, question, answer):
    try:
        with connection.cursor() as cursor:
            # Fetch the existing user data
            cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
            existing_data = cursor.fetchone()

            if existing_data['question'] is None and existing_data['answer'] is None:
                # If the user's question and answer fields are null, update the existing row
                cursor.execute("UPDATE users SET question=%s, answer=%s WHERE id=%s", (question, answer, user_id))
                print("Question and answer updated successfully!")
            else:
                # If the user already has existing question and answer, insert a new row
                cursor.execute("""
                    INSERT INTO users (user_id, username, password, question, answer)
                    VALUES (%s, %s, %s, %s, %s)
                """, (existing_data['user_id'], existing_data['username'], existing_data['password'], question, answer))
                print("New row inserted with updateda question and answer.")
                
            connection.commit()
    except Exception as e:
        print("An error occurred:", str(e))
        
import pymysql

def print_table_by_user_id():
    try:
        # Connect to your MySQL database
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='abkmysql',
            database='chat'
        )

        with connection.cursor() as cursor:

            user_id = input("Enter user ID: ")

            query = "SELECT question, answer FROM users WHERE user_id = %s"
            print("Executing SQL query:", query)
            cursor.execute(query, (user_id,))
            
            rows = cursor.fetchall()
            print("Fetched rows:")
        
            for row in rows:
                question, answer = row
                print("Question:", question)
                print("Answer:", answer)
                print()

    except Exception as e:
        print("Error:", e)
    finally:
        # Close the database connection
        connection.close()



def main():
    # user_info = login()
    # if user_info[0] is not None:
    #     print("User ID:", user_info[0])
    while True:
        print("\n1. Signup")
        print("2. Login")
        print("3. Print table")
        print("4. Fetch all questions and answers")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            signup()
        elif choice == '2':
            user_id, username, hashed_password = login()
            if user_id:
                question = input("Enter your question: ")
                
                answer = answer_question_from_pdf("/Users/macbook/Desktop/multiusrdb/docs/ISO+13485-2016.pdf", question)
                update_question_and_answer(user_id, question, answer)

                print("Question and answer added successfully!")
            else:
                print("Failed to retrieve answer.")
        elif choice == '3':
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM users")
                users_data = cursor.fetchall()
                print("Users Table:")
                print_table(users_data)
        elif choice == '4':
            print_table_by_user_id()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

    connection.close()

if __name__ == "__main__":
    main()

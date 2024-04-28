# import os
# # Generate a random string of 24 characters
# secret_key = os.urandom(24)
# # Print the secret key
# print(secret_key)

# from flask import Flask, render_template, request, redirect, url_for, session
# app = Flask(__name__)
# app.secret_key = b'\xfd\x9dd\xfbN\xfa\xca\xd7\x0f\x84\x8f~\xc6yd\t\xe3\x1c \x8b\x8c;\xbc\xda'

import pymysql, logging
from iso_qa_export import answer_question_from_pdf



# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'abkmysql',
    'database': 'all_users'  # Parent database name to contain all user databases
}

# Function to create the parent database and user table
def create_parent_database():
    connection = pymysql.connect(host=db_config['host'], user=db_config['user'], password=db_config['password'])
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS all_users")
        cursor.execute("USE all_users")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                phone_number VARCHAR(20) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL
            )
        """)
    connection.commit()
    connection.close()

# Function to create a new table for a user to store their questions and answers
def create_user_table(phone_number):
    connection = pymysql.connect(**db_config)
    with connection.cursor() as cursor:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS user_{phone_number} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL
            )
        """)
    connection.commit()
    connection.close()

# Function to register a new user
def register_user(name, phone_number, password):
    create_parent_database()  # Ensure 'all_users' database and 'users' table exist
    create_user_table(phone_number)
    connection = pymysql.connect(**db_config)
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO users (name, phone_number, password) 
            VALUES (%s, %s, %s)
        """, (name, phone_number, password))
    connection.commit()
    connection.close()
    print(f"User with phone number '{phone_number}' created successfully.")

# Function to validate login
def validate_login(phone_number, password):
    connection = pymysql.connect(**db_config)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM all_users.users WHERE phone_number = %s AND password = %s
        """, (phone_number, password))
        user = cursor.fetchone()
        if user:
            # Print login success message
            print(f"Login successful for user with phone number '{phone_number}'.")

            # Fetch the user's table name
            user_table_name = f"user_{phone_number}"

            # Execute query to retrieve content of the user's table
            cursor.execute(f"SELECT * FROM {user_table_name};")
            table_content = cursor.fetchall()

            # Print the content of the user's table
            print(f"Content of table '{user_table_name}':")
            for row in table_content:
                print(row)

            return True
        else:
            # Print login failure message
            print(f"Login failed for user with phone number '{phone_number}'.")
            return False

    connection.close()
    
    
    
def save_to_database(phone_number, question, answer):

    # Connect to the database
    connection = pymysql.connect(**db_config)

    try:
        with connection.cursor() as cursor:
            # Create table for the user if not exists
            user_table_name = f"user_{phone_number}"
            create_table_sql = f"CREATE TABLE IF NOT EXISTS {user_table_name} (id INT AUTO_INCREMENT PRIMARY KEY, question VARCHAR(255) NOT NULL, answer VARCHAR(255) NOT NULL)"

            cursor.execute(create_table_sql)

            # Insert question and answer into user's table
            insert_data_sql = f"INSERT INTO {user_table_name} (question, answer) VALUES (%s, %s)"
            cursor.execute(insert_data_sql, (question, answer))
            connection.commit()

            print("Question and answer inserted successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close connection
        connection.close()
        
def print_stored_chat(phone_number):
    # Connect to the database
    connection = pymysql.connect(**db_config)

    try:
        with connection.cursor() as cursor:
            # Fetch stored chat from the user's table
            user_table_name = f"user_{phone_number}"
            select_data_sql = f"SELECT * FROM {user_table_name}"
            cursor.execute(select_data_sql)
            stored_chat = cursor.fetchall()

            # Print the stored chat
            print("Stored Chat:")
            for row in stored_chat:
                print(f"Question: {row[1]}, Answer: {row[2]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close connection
        connection.close()
    


def main():
    while True:
        print("Welcome to the Terminal Authentication System")
        print("1. Signup")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice (1, 2, or 3): ")

        if choice == '1':
            # Signup process
            name = input("Enter your name: ")
            phone_number = input("Enter your phone number: ")
            password = input("Enter your password: ")

            # Register the user
            register_user(name, phone_number, password)
            print("Signup successful! You can now login.")
        elif choice == '2':
            # Login process
            phone_number = input("Enter your phone number: ")
            password = input("Enter your password: ")

            # Validate login
            if validate_login(phone_number, password):
                print("Login successful!")
                while True:
                    print_stored_chat(phone_number)
                    # Call the function to answer question from PDF
                    file = "/Users/macbook/Desktop/multiusrdb/docs/ISO+13485-2016.pdf"
                    user_question = input("Enter your question: ")
                    ans = answer_question_from_pdf(file, user_question)
                    print(ans)
                    save_to_database(phone_number, user_question, ans)
                    print_stored_chat(phone_number)
                    
                    # Ask if the user wants to continue or exit
                    option = input("Type 'exit' to logout or press Enter to continue answering questions: ")
                    if option.lower() == 'exit':
                        break
                continue  # Ask for option 1 or 2 again
            else:
                print("Invalid phone number or password. Please try again.")
        elif choice == '3':
            print("Exiting the Terminal Authentication System. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

        # Ask for option 1 or 2 again
        print("\n")
        print("Would you like to:")
        print("1. Signup")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice (1, 2, or 3): ")


if __name__ == '__main__':
    main()
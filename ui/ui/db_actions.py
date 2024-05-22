'''Signup New Users'''

import streamlit as st
from streamlit_authenticator.utilities.hasher import Hasher
import datetime
import re
import os
from sqlmodel import Field, SQLModel, create_engine, Session, select
import psycopg2



# Get Secret values from you OS Environment
db_name = "todo_db"
db_pass = "oVicMndBI84f"

# A table of Users in Database
class Users(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    email: str
    username: str
    hash_password: str

# Setting up DB Connectivity

conn_string = f"postgresql://todo_db_owner:{db_pass}@ep-ancient-bread-a5kwtqzb.us-east-2.aws.neon.tech/{db_name}?sslmode=require"

def createEngineFunction():
    try:
        engine = create_engine(conn_string)
        SQLModel.metadata.create_all(engine)
        return engine
        # st.write("Connected to Database")
    except Exception as e:
        st.write(e)

engine = createEngineFunction()

def insert_user(email, username, hashed_password):
    user = Users(email=email, username=username, hash_password=hashed_password)
    session = Session(engine)
    session.add(user)
    session.commit()


def fetch_users():
    '''Fetching all users from the database'''
    users_all = []
    session = Session(engine)
    statement = select(Users)
    results = session.exec(statement)
    for i in results:
        users_all.append(i)
    return users_all


def validate_email(email):
    '''Validating that entered email is of correct format'''

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False
    
def validate_username(username):
    '''Validating that entered username is of correct format'''
    pattern = "^[a-zA-Z0-9]*$"
    if re.match(pattern, username):
        return True
    return False


def get_user_emails():
    '''Getting all emails from the database'''
    emails_in_db = []
    with Session(engine) as session:
        statement = select(Users.email)
        results = session.exec(statement)
        for i in results:
            # print(i)
            emails_in_db.append(i)
    return emails_in_db

def get_usernames():
    '''Getting all usernames from the database'''
    usernames_in_db = []
    with Session(engine) as session:
        statement = select(Users.username)
        results = session.exec(statement)
        for i in results:
            # print(i)
            usernames_in_db.append(i)
    return usernames_in_db


def sign_up(col2):
    success = False
    # col1, col2 = st.columns(2)
    with col2:
        with st.form(key="signup", clear_on_submit=True):
            st.subheader(':green[Sign Up]')
            email = st.text_input('Email', placeholder="Enter You Email")
            username = st.text_input('Username', placeholder="Enter Your Username")
            password1 = st.text_input('Password', placeholder="Enter Your Password", type="password")
            password2 = st.text_input('Confirm Password', placeholder="Confirm Your Password", type="password")

            if email:
                if validate_email(email): #Validating that entered email is of correct format
                    if email not in get_user_emails(): # Checking that same email is not already in use
                        if validate_username(username):
                            if username not in get_usernames():
                                if len(username) > 2:
                                    if len(password1) >= 6:
                                        if password1 == password2:
                                            hashed_password = Hasher([password1]).generate()
                                            # Add User to the Database
                                            try:
                                                insert_user(email, username, hashed_password[0])
                                                st.success('Account Created Successfully!')
                                                success = True
                                            except Exception as e:
                                                st.error("Internal Error Occurred")
                                        else:
                                            st.warning('Passwords do not match!')
                                    else:
                                        st.warning('Password is too Short')
                                else:
                                    st.warning('Username is too Short')
                            else:
                                st.warning('Username Already Exist!')
                        else:
                            st.warning('Invalid Username')
                    else:
                        st.warning('Email Already Exist!')
                else:
                    st.error('Invalid Email')

            btn1, btn2, btn3 = st.columns(3)  #Centering Signup Button in Form
            with btn2:
                st.form_submit_button('Sign Up')

    if success:
        return True
    else:
        return False

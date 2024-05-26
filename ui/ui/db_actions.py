'''Signup New Users'''

import streamlit as st
from streamlit_authenticator.utilities.hasher import Hasher
import datetime
import re
import os
from sqlmodel import Field, SQLModel, create_engine, Session, select
import psycopg2
import settings


# Setting up DB Connectivity

# For NeonTech DB 
# db_name = "todo_db"
# db_pass = "oVicMndBI84f"
# conn_string = f"postgresql://todo_db_owner:{db_pass}@ep-ancient-bread-a5kwtqzb.us-east-2.aws.neon.tech/{db_name}?sslmode=require"

conn_string = str(settings.DATABASE_URL)


# A table of Users in Database
class Users(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    email: str
    username: str
    hash_password: str

# A table of ToDo Items in Database for Every User
class ToDos(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}  #If Table Already Exists, Append to that table
    id: int | None = Field(default=None, primary_key=True)
    username: str
    title: str
    description: str
    target_date: str
    completed: bool


def createEngineFunction():
    try:
        engine = create_engine(conn_string, pool_size=10, max_overflow=20)
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



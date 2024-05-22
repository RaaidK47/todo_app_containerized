'''Signup New Users'''

import streamlit as st
from streamlit_authenticator.utilities.hasher import Hasher
import datetime
import re
import os
from sqlmodel import Field, SQLModel, create_engine, Session, select
import psycopg2





SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



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



'''Signup New Users'''

import streamlit as st
from streamlit_authenticator.utilities.hasher import Hasher
import datetime
import re
import os
# from sqlmodel import Field, SQLModel, create_engine, Session, select
import psycopg2
# import settings


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





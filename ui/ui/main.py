'''Main Streamlit Application'''
import streamlit as st
import streamlit_authenticator as stauth
from db_actions import validate_email, get_user_emails, validate_username, get_usernames, insert_user
from streamlit_authenticator.utilities.hasher import Hasher
import time
from streamlit_extras.stylable_container import stylable_container
import cssStyles as cssStyles
import requests
from streamlit_cookies_manager import EncryptedCookieManager


import warnings
warnings.filterwarnings("ignore")



BASE_URL = "http://172.17.0.1:8000"  # BASE URL of Docker Container
# BASE_URL = "http://127.0.0.1:8000"     # BASE URL of Local PC

def wide_space_default():
    st.set_page_config(layout="wide")

wide_space_default()

cookies = EncryptedCookieManager(prefix="myapp_", password="password_here")
if not cookies.ready():
    st.stop()

if 'token' not in st.session_state and 'token' in cookies:
    st.session_state.token = cookies['token']

elif 'token' not in st.session_state and 'token' not in cookies:
    st.session_state.token = None

def login():
    col1, col2 = st.columns(2)
    
    with col1:
        placeholder_title = st.empty()
        login_form = st.empty()
        placeholder_title.header("ToDo App") # Adding Extra Space

        with login_form.form(key="login", clear_on_submit=True):
            st.subheader(':blue[Log In]')
            username_login = st.text_input('Username', placeholder="Enter Your Username")
            password = st.text_input('Password', placeholder="Enter Your Password", type="password")

            with stylable_container(
                key="login-button",
                css_styles=[cssStyles.login_button, cssStyles.login_button_hover],):
        
                submitted = st.form_submit_button('Login')
                
                if submitted:
                    response = requests.post(f"{BASE_URL}/token", data={"username": username_login, 
                                                                    "password": password})
                
                    if response.status_code == 200:
                        st.success("Login Successful")
                        

                        access_token = response.json()["access_token"]
                        token_type = response.json()["token_type"]

                        cookies['token'] = access_token
                        cookies['username'] = username_login
                        cookies.save()

                        st.session_state.token = access_token

                        st.rerun()
                        
                    else:
                        st.error("Username / Password is Incorrect")


    with col2:
        signup_form = st.empty()
        with signup_form.form(key="signup", clear_on_submit=True):
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



if st.session_state.token:
    from app import main ; main(cookies['username'])

    sideb = st.sidebar
    # Designing Sidebar
    with sideb:
        _, _, col, _, _, _,_  = st.columns(7)
        with col:
            with stylable_container(
                key="logout-button",
                css_styles=[cssStyles.logout_button, cssStyles.logout_button_hover],):

                log_out = st.button('Log Out')

                if log_out:
                    st.session_state.token = None
                    cookies['token'] = ''
                    cookies.save()
                    st.experimental_rerun()

else:
    login()
                        

    

'''Main Streamlit Application'''
import streamlit as st
import streamlit_authenticator as stauth
from db_actions import validate_email, validate_username
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

    st.write("**Developed By:**  M. Raaid Khan")
    with col2:
        signup_form = st.empty()
        with signup_form.form(key="signup", clear_on_submit=True):
            st.subheader(':green[Sign Up]')
            email = st.text_input('Email', placeholder="Enter You Email")
            username = st.text_input('Username', placeholder="Enter Your Username")
            password1 = st.text_input('Password', placeholder="Enter Your Password", type="password")
            password2 = st.text_input('Confirm Password', placeholder="Confirm Your Password", type="password")

            btn1, btn2, btn3 = st.columns(3)  #Centering Signup Button in Form
            with btn2:
                submitted = st.form_submit_button('Sign Up')
                
            if submitted:
                if not email:
                    st.warning('Enter Email')
                    return
                elif not username:
                    st.warning('Enter Username')

                elif not password1:
                    st.warning('Enter Password')
                    return
                elif not password2:
                    st.warning('Confirm Password')

                if not validate_email(email):
                    st.warning('Invalid Email')
                
                elif not validate_username(username):
                    st.warning('Invalid Username')
                
                elif len(username) < 3:
                    st.warning('Username is too Short')

                
                elif password1 != password2:
                    st.warning('Passwords do not match!')

                
                elif len(password1) < 6:
                    st.warning('Password is too Short')


                else:
                    hashed_password = Hasher([password1]).generate()
                    hashed_password = hashed_password[0]

                    response = requests.post(f"{BASE_URL}/create_user", json={"username": username,
                                                                        "email": email,
                                                                        "hash_password": hashed_password})

                    if response.status_code == 200:
                        st.success("Account Created Successfully!")

                    else:
                        response_detail = response.json()
                        detail_text = response_detail.get("detail", "No detail provided.")
                        st.error(f"Error: {detail_text}")


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
                    st.rerun()

else:
    login()
                        

    

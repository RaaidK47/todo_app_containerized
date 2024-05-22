'''Main Streamlit Application'''
import streamlit as st
import streamlit_authenticator as stauth
from db_actions import validate_email, get_user_emails, validate_username, get_usernames, insert_user
from streamlit_authenticator.utilities.hasher import Hasher
import time
from streamlit_extras.stylable_container import stylable_container
import cssStyles as cssStyles
import requests

# BASE_URL = "http://172.17.0.1:8000"  # BASE URL of Docker Container
BASE_URL = "http://127.0.0.1:8000"     # BASE URL of Local PC

def wide_space_default():
    st.set_page_config(layout="wide")

wide_space_default()

    

st.session_state["token"] = False

col1, col2 = st.columns(2)
with col1:
    placeholder_title = st.empty()
    placeholder_title.header("ToDo App") # Adding Extra Space

    login_form = st.empty()

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
                st.session_state["token"] = True
                

            else:
                st.error("Username / Password is Incorrect")
                st.session_state["token"] = False


        # Authenticator = stauth.Authenticate(credentials, cookie_name='Streamlit', cookie_key='abcdef', cookie_expiry_days=4)
        # email, authentication_status, username = Authenticator.login(fields={'Form name':'Login', 'Username':'Username', 'Password':'Password', 'Login':'Login'}, location='main')


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
                                            time.sleep(2)
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



if st.session_state["token"]:
    placeholder_title.empty() 
    login_form.empty()
    signup_form.empty()

    from app import main ; main(username_login) 

    def logout():
        st.session_state["token"] = False
        print("Logout")
    
    sideb = st.sidebar
    # Designing Sidebar
    with sideb:
        _, _, col, _, _, _,_  = st.columns(7)
        with col:
            with stylable_container(
                key="logout-button",
                css_styles=[cssStyles.logout_button, cssStyles.logout_button_hover],):

                st.button('Log Out', on_click=logout)

    
    



    

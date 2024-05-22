'''Main Streamlit Application'''
import streamlit as st
import streamlit_authenticator as stauth
from db_actions import sign_up, fetch_users
import time
from streamlit_extras.stylable_container import stylable_container
import cssStyles as cssStyles

def wide_space_default():
    st.set_page_config(layout="wide")

wide_space_default()

@st.cache_data  # Cache the data, This function will run only once
def get_users():
    try:
        print("Getting Users")
        users = fetch_users()
        emails = []
        usernames = []
        passwords = []  

        print(len(users))

        for user in users:
            emails.append(user.email)
            usernames.append(user.username)
            passwords.append(user.hash_password)

        credentials = {'usernames': {}}

        for index in range(len(emails)):
            credentials['usernames'][usernames[index]] = {'name': emails[index], 'password': passwords[index]}

        
        # print(credentials)
        return credentials, True
    
    except Exception as e:
        # print(e)
        return None, False

credentials, isUsers = get_users() 

if isUsers is True:
    # print("Creating Authenticator")
    col1, col2 = st.columns(2)
    with col1:
        placeholder_title = st.empty()
        placeholder_title.header("ToDo App") # Adding Extra Space
        Authenticator = stauth.Authenticate(credentials, cookie_name='Streamlit', cookie_key='abcdef', cookie_expiry_days=4)
        email, authentication_status, username = Authenticator.login(fields={'Form name':'Login', 'Username':'Username', 'Password':'Password', 'Login':'Login'}, location='main')


info, info1 = st.columns(2)

if not authentication_status: 
    # authentication_status = True >> if user is authenticated
    # authentication_status = False >> if user is not authenticated
    
    newUser = sign_up(col2)  # Show the Signup Portion of Application 

    if newUser:
        print("New User Created")
        st.cache_data.clear()  # Clear Cache data to the Updated Users are Fetched from DB



if st.session_state["authentication_status"]:
    # Importing Function and Calling in Same Line
    placeholder_title.empty() 
    from ui import main ; main(username) 

    def logout():
        print("Logout")
        Authenticator.authentication_handler.execute_logout()
        Authenticator.cookie_handler.delete_cookie()
    
    sideb = st.sidebar
    # Designing Sidebar
    with sideb:
        _, _, col, _, _, _,_  = st.columns(7)
        with col:
            with stylable_container(
                key="logout-button",
                css_styles=[cssStyles.logout_button, cssStyles.logout_button_hover],):

                st.button('Log Out', on_click=logout)
            # Authenticator.logout('Log Out', 'sidebar')
    
elif st.session_state["authentication_status"] is False:
    with info:
        st.error('Username / Password is Incorrect')


    

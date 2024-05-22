import streamlit as st
import json
import logging
from streamlit.logger import get_logger as getLogger
import datetime
import time
import requests
from streamlit_extras.stylable_container import stylable_container
import cssStyles as cssStyles
from todos import to_do



BASE_URL = "http://172.17.0.1:8000"  # BASE URL of Docker Container

@st.experimental_dialog("Create ToDo Item")
def todoDialog(username):
    with st.form(key="ToDoForm", clear_on_submit=True):
        todo_title = st.text_input(r"$\textsf{\Large Title}$", placeholder="Title of ToDo Task")  # Using LATEX to show large title of text_input
        todo_description = st.text_area(r"$\textsf{\Large Description}$", placeholder="Description of ToDo Task") 
        target_date = st.date_input(r"$\textsf{\Large Target Date}$", datetime.date.today(), min_value=datetime.date.today())

        btn1, btn2, btn3 = st.columns(3)  #Centering Button in Form
        with btn2:
            submitted = st.form_submit_button('Add ToDo Item')
            
        if submitted:
            if todo_title == "" or todo_description == "" or target_date == "":
                st.warning("Please Fill All Fields")
            else:
                response = requests.post(f"{BASE_URL}/todos/", json={"username": username, 
                                                                     "title": todo_title, 
                                                                     "description": todo_description, 
                                                                     "target_date": str(target_date),
                                                                     "completed": False })
                print(response)
                if response.status_code == 200:
                    st.success("ToDo Created")
                    # time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"Unable to Create ToDo due to Status Code {response.status_code}")

def delete_todo(id, username):
    response = requests.delete(f"{BASE_URL}/todos/{id}")
    if response.status_code == 200:
        print("ToDo Deleted Successfully")
        # time.sleep(2)
        # st.rerun()
    else:
        st.error(f"Unable to Delete ToDo due to Status Code {response.status_code}")

def update_request(username, todo_title_updt, todo_description_updt, target_date_updt):
    print("Update Function Called")
    print(todo_title_updt)
    print(todo_description_updt)
    print(target_date_updt)
    if todo_title_updt == "" or todo_description_updt == "" or target_date_updt == "":
        st.warning("Please Fill All Fields")
    else:
        print("Updating ToDo")
        response = requests.put(f"{BASE_URL}/todos/{id}", json={"username": username,
                                                                 "title": todo_title_updt, 
                                                                 "description": todo_description_updt, 
                                                                 "target_date": str(target_date_updt)})
        print(response)
        if response.status_code == 200:
            st.success("ToDo Updated!")
            time.sleep(2)
            st.rerun()
        else:
            st.error(f"Unable to Update ToDo due to Status Code {response.status_code}")

@st.experimental_dialog("Update ToDo Item")
def update_todo(id, username, todo):
    print("Update ToDo Function Called")
    todoTitle = todo['title']
    todoDescription = todo['description']
    targetDate = todo['target_date']
    datetime_targetDate = datetime.datetime.strptime(targetDate, '%Y-%m-%d').date()

    with st.form(key="ToDoUpdateForm", clear_on_submit=False):
        title_update = st.text_input(r"$\textsf{\Large Title}$", value=todoTitle, key="update_title")
        description_update = st.text_area(r"$\textsf{\Large Description}$", value=todoDescription, key="update_description") 
        target_date_update = st.date_input(r"$\textsf{\Large Target Date}$", 
                                           value=datetime_targetDate if datetime_targetDate >= datetime.date.today() else datetime.date.today(), 
                                           min_value=datetime.date.today(), key = "update_date")
        
        _, col, _ = st.columns(3)   

        with col:
            submitted = st.form_submit_button('Update ToDo')

        if submitted:
            
            if title_update == "":
                title_update = todoTitle

            if description_update == "":
                description_update = todoDescription
                
            
            response = requests.put(f"{BASE_URL}/todos/{id}", json={"username": username, 
                                                                    "title": title_update, 
                                                                    "description": description_update, 
                                                                    "target_date": str(target_date_update)})
            # print(response)
            if response.status_code == 200:
                st.success("ToDo Updated!")
                time.sleep(2)
                st.rerun()
            else:
                st.error(f"Unable to Update ToDo due to Status Code {response.status_code}")
    

def get_todos(username):
    prev_todos_status = {}
    response = requests.get(f"{BASE_URL}/todos/", {"username": username})

    response_list = response.json()

    # Sort Reponses by ID to maintain Order after Updates
    reponse_list_sorted = sorted(response_list, key=lambda d: d['id'])


    # print(response.json())
    if not reponse_list_sorted:
        st.text("No ToDo Items")
    else:
        todos_status = {}
        for i in reponse_list_sorted:
            # print(i)
            title = i['title']
            description = i['description']
            target_date = i['target_date']
            id = i['id']
            completed = i['completed']

            prev_todos_status[str(id)] = completed

            col1 , col2 = st.columns([4,1])
            with col1:
                with stylable_container(
                key="container_with_border",
                css_styles=cssStyles.todoContainer
                # css_styles=
                ,):

                    todo_check = to_do([(st.write, title),
                            (st.markdown, f"""**Description:** *{description}*"""),
                            (st.markdown, f"""**Target Date:** {target_date}"""),
                        ],
                        checkbox_id=str(id),
                        check_bool=completed,
                    )

            todos_status[str(id)] = todo_check   # e.g. {'9': False, '10': False}
 
            with col2:
                # st.markdown("")
                with stylable_container(
                    key="delete-button",
                    css_styles=[cssStyles.delete_button],):
                    st.button("Delete", key="btn_del_todo_"+str(id), on_click=delete_todo, args=(id, username))
                

                with stylable_container(
                    key="update-button",
                    css_styles=[cssStyles.update_button, cssStyles.update_button_hover],):  # Passing Multiple CSS Styles as List
                    submitted = st.button("Update", key="btn_upd_todo_"+str(id))
                    
                if submitted:
                    # print(id)
                    # print(username)
                    update_todo(id, username, next((item for item in response.json() if item['id'] == id), None))

        if (prev_todos_status == todos_status):
            print("todos Not Changed")
            pass
        
        else:
            print("todos Changed")
            diff = {}
            for key in prev_todos_status.keys() | todos_status.keys():
                if prev_todos_status.get(key) != todos_status.get(key):
                    diff[key] = (prev_todos_status.get(key), todos_status.get(key))
            print(diff)  # e.g {'27': (False, True)}


            key, value = list(diff.items())[0]
            print(key, value[0], value[1])  # key = id

            response = requests.patch(f"{BASE_URL}/todos/{key}", json={"completed": value[1]})
            # print(response)
            if response.status_code == 200:
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"Unable to Update ToDo due to Status Code {response.status_code}")


        # print(todos_status)

def reduceTopWhitespace():
    st.markdown(
        """
            <style>
                .appview-container .main .block-container {{
                    padding-top: {padding_top}rem;
                    padding-bottom: {padding_bottom}rem;
                    }}

            </style>""".format(
            padding_top=0, padding_bottom=1
        ),
        unsafe_allow_html=True,
    )

def reduceSidebarTopWhitespace():
    st.markdown(
        """
            <style>
                .sidebar .stSideBar {{
                        margin-top: {margin_top}rem;
                        padding-top: {padding_top}rem;
                    }}

            </style>""".format(
            padding_top=0, margin_top=0
        ),
        unsafe_allow_html=True,
    )

def main(username):
    app_logger = getLogger(__file__)
    app_logger.setLevel(logging.INFO)

    reduceTopWhitespace()
    reduceSidebarTopWhitespace()
    
    st.header("My ToDo List")
    
    sideb = st.sidebar
    # Designing Sidebar
    with sideb:
        
        with stylable_container(
            key="sidebar-header_text",
            css_styles=cssStyles.sidebar_header_text,):

            st.write(f'Welcome, '+ str(username).capitalize())
            st.write("")


        st.header("")
        
        _, col , _ = st.columns([1, 3, 1])
        with col:
            with stylable_container(
                key="create-button",
                css_styles=[cssStyles.create_button, cssStyles.create_button_hover],):
                create_button = st.button("Create Todo Item")
        
        st.header("")
        st.header("")
        st.header("")

    get_todos(username)

    
    app_logger.info("App Refreshed")

    # Showing Create ToDo Dialog
    if create_button:
        todoDialog(username)  

    
    


        
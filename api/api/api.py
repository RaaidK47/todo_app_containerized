from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, SQLModel, create_engine, Session, select
import psycopg2
import os
import json

from typing import Annotated, Union
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import logging
from starlette.middleware.cors import CORSMiddleware
import api.settings as settings

import asyncio
from aiokafka import AIOKafkaProducer


logging.getLogger('passlib').setLevel(logging.ERROR) # To Suppress bcrypt Warnings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "cb96bd461cb3262adc143a16023c243ce09cae5a6b52db99dc12a8ca128edd0f"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# Kafka Configuration
KAFKA_TOPIC = "your_topic"
KAFKA_BOOTSTRAP_SERVERS = "broker:19092"

async def produce_messages(message):
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v.decode('utf-8')).encode('utf-8') if isinstance(v, bytes) else json.dumps(v).encode('utf-8')
    )
    await producer.start()
    try:
        await producer.send_and_wait(KAFKA_TOPIC, json.dumps(message).encode('utf-8'))
        # print(f"Produced message: {message}")
    finally:
        await producer.stop()


# CORS Middleware is required for CORS Issue
# When running FastAPI in Docker & Swagger in Local Computer
app.add_middleware(CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
expose_headers=["*"])

# A table of ToDo Items in Database for Every User
class ToDos(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}  #If Table Already Exists, Append to that table
    id: int | None = Field(default=None, primary_key=True)
    username: str
    title: str
    description: str
    target_date: str
    completed: bool

# A table of Users in Database
class Users(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}
    id: int | None = Field(default=None, primary_key=True)
    email: str
    username: str
    hash_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

# conn_string = f"postgresql://todo_db_owner:{db_pass}@ep-ancient-bread-a5kwtqzb.us-east-2.aws.neon.tech/{db_name}?sslmode=require"
conn_string = str(settings.DATABASE_URL)

def createEngineFunction():
    try:
        engine = create_engine(conn_string, pool_size=10, max_overflow=20)
        SQLModel.metadata.create_all(engine)
        return engine
        # st.write("Connected to Database")
    except Exception as e:
        print(e)

engine = createEngineFunction()

def create_session():
    with Session(engine) as session:
        yield session


@app.get("/")
async def hello():
    await produce_messages({'Info':'Base API Accessed'})
    return {"Hello": "World"}

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

class UserInDB(Users):
    hashed_password: str

def get_user(users_all, username: str):

    for i in users_all:
        if username == i.username:
            return i 

def authenticate_user(users_all, username: str, password: str):
    user = get_user(users_all, username)
    if not user:
        print("User not found")
        return False
    if not verify_password(password, user.hash_password):
        print("Password not matched")
        return False
    return user

def fetch_users():
    '''Fetching all users from the database'''
    users_all = []
    session = Session(engine)
    statement = select(Users)
    results = session.exec(statement)
    for i in results:
        users_all.append(i)
    return users_all

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    users_all = fetch_users()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(users_all, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[Users, Depends(get_current_user)],
):
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/create_user")
async def create_user(user: Users,
                       db: Session = Depends(create_session)):
    '''Create a New User in the Database'''

    await produce_messages({'Info':'Create User Request Received'})

    email = str(user.email)
    username = str(user.username)
    hashed_password = str(user.hash_password) 

    print(email)
    print(username)
    print(hashed_password)
        
    def get_user_emails():
        '''Getting all emails from the database'''
        emails_in_db = []
        
        statement = select(Users.email)
        results = db.exec(statement)
        for i in results:
            # print(i)
            emails_in_db.append(str(i).lower())

        return emails_in_db
    
    
    def get_usernames():
        '''Getting all usernames from the database'''
        usernames_in_db = []
        
        statement = select(Users.username)
        results = db.exec(statement)
        for i in results:
            # print(i)
            usernames_in_db.append(str(i).lower())
        return usernames_in_db


    if str(email).lower() not in get_user_emails(): # Checking that same email is not already in use
        
        if str(username).lower() not in get_usernames():
            try:
                user = Users(email=email, username=username, hash_password=hashed_password)
                db.add(user)
                db.commit()
                db.refresh(user)
                # return user
                await produce_messages({'Success':f'User with username *{username}* created successfully!'})
                return True
            except Exception as e:
                await produce_messages({'Error':f'Unable to create user due to internal error'})
                return False
        else:
            await produce_messages({'Error':f'Username *{username}* already exist'})
            raise HTTPException(status_code=400, detail="Username Already Exist")
        
    else:
        await produce_messages({'Error':f'Email *{email}* already exist'})
        raise HTTPException(status_code=400, detail="Email Already Exist")

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    print(form_data.username)
    print(form_data.password)
    users_all = fetch_users()
    user = authenticate_user(users_all, form_data.username, form_data.password)
    if not user:
        await produce_messages({'Error':f'Incorrect username or password for user *{form_data.username}*'})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    print("Token Generated")
    await produce_messages({'Success':f'Token Generated for User *{user.username}*'})
    return Token(access_token=access_token, token_type="bearer")

@app.get("/users/me/", response_model=Users)
async def read_users_me(
    current_user: Annotated[Users, Depends(get_current_active_user)],
):
    '''Get Currently Active User'''
    return current_user

@app.get("/users/me/todos/")
async def get_todos_user(
    current_user: Annotated[Users, Depends(get_current_active_user)]
):
    '''Returning ToDos for User that is 
    currently Logged In'''
    session = Session(engine)
    current_user.username = str(current_user.username).lower()
    print(current_user.username)

    statement = select(ToDos).where(ToDos.username == current_user.username)
    # print(statement)
    results = session.exec(statement)
    # print(results.all())
    await produce_messages({'Info':f'ToDos for User *{current_user.username}* were retreived'})
    return results.all()




@app.post("/users/me/todos/")
async def create_todo(current_user: Annotated[Users, Depends(get_current_active_user)],
                todo: ToDos, 
                db: Session = Depends(create_session)
):
    '''Create a New ToDo Item for the
    User that is currently Logged In'''

    print("ToDo Created for User: " + current_user.username)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    await produce_messages({'Success':f'ToDo Created for User *{current_user.username}* '})
    return todo


@app.put("/users/me/todos/{todo_id}")
async def update_todo(current_user: Annotated[Users, Depends(get_current_active_user)],
                todo_id: int, 
                updated_todo: ToDos, 
                db: Session = Depends(create_session)):
    
    '''Updating ToDo Item for the User that is
    currently Logged In'''

    statement = select(ToDos).where(ToDos.id == todo_id)
    results = db.exec(statement)
    todo = results.one()

    if todo is None:
        await produce_messages({'Error':f'ToDo for User {current_user.username} not found'})
        raise HTTPException(status_code=404, detail="Todo not found")

    if(todo.username == str(current_user.username).lower()):
        todo.title = updated_todo.title
        todo.description = updated_todo.description
        todo.target_date = updated_todo.target_date

        db.add(todo)
        db.commit()
        await produce_messages({'Success':f'ToDo for User {current_user.username} updated successfully'})
        db.refresh(todo)
        return True

    else:
        print("You are not authorized to updated this ToDos")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not Authorized to Update this ToDo",
        )



@app.patch("/users/me/todos/{todo_id}")
async def update_todo_completed(current_user: Annotated[Users, Depends(get_current_active_user)],
                          todo_id: int, todo_updated:ToDos, 
                          db: Session = Depends(create_session)):
    # print(todo_updated)
    '''Updating ToDo Item Completion Status
    for the User that is currently Logged In'''
    statement = select(ToDos).where(ToDos.id == todo_id)
    results = db.exec(statement)
    todo = results.one()

    if todo is None:
        await produce_messages({'Error':f'ToDo for User {current_user.username} not found'})
        raise HTTPException(status_code=404, detail="Todo not found")

    if(todo.username == str(current_user.username).lower()):
        todo.completed = todo_updated.completed

        db.add(todo)
        db.commit()
        db.refresh(todo)
        await produce_messages({'Success':f'Completion Status for ToDo <{todo_id}> of User {current_user.username} updated successfully'})
        return True
    
    else:
        print("You are not authorized to Update Completion Status this ToDos")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not Authorized to change ToDo",
        )


@app.delete("/users/me/todos/{todo_id}")
async def delete_todo(current_user: Annotated[Users, Depends(get_current_active_user)],
                todo_id: int, 
                db: Session = Depends(create_session)):
    '''Deleting ToDo Item for the User that is
    currently Logged In'''

    statement = select(ToDos).where(ToDos.id == todo_id)
    results = db.exec(statement)
    todo = results.one()

    if todo is None:
        await produce_messages({'Error':f'ToDo for User {current_user.username} not found'})
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if (todo.username == str(current_user.username).lower()):
        db.delete(todo)
        db.commit()
        await produce_messages({'Success':f'ToDo <{todo_id}> for User {current_user.username} deleted successfully'})
        return {"message": "Todo deleted successfully"}
    
    else:
        print("You are not authorized to Delete this ToDos")
        await produce_messages({'Error':f'User not Authorized to Delete ToDo'})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not Authorized to change ToDo",
        )


# @app.get("/todos/")
# def retrieve_todos(username = ToDos.username, db: Session = Depends(create_session)):
#     # print(username)
#     statement = select(ToDos).where(ToDos.username == username)
#     # print(statement)
#     results = db.exec(statement)
#     # print(results.all())
#     return results.all()

# @app.post("/todos/")
# def create_todo(todo: ToDos, db: Session = Depends(create_session)):
#     db.add(todo)
#     db.commit()
#     db.refresh(todo)
#     return todo

# @app.get("/todos/{todo_id}")
# def get_todo_id(todo_id: int, db: Session = Depends(create_session)):
#     todo = db.get(ToDos, todo_id)
#     if todo is None:
#         raise HTTPException(status_code=404, detail="Todo not found")
#     return todo

# @app.put("/todos/{todo_id}")
# def update_todo(todo_id: int, updated_todo: ToDos, db: Session = Depends(create_session)):
#     statement = select(ToDos).where(ToDos.id == todo_id)
#     results = db.exec(statement)
#     todo = results.one()

#     todo.title = updated_todo.title
#     todo.description = updated_todo.description
#     todo.target_date = updated_todo.target_date

#     db.add(todo)
#     db.commit()
#     db.refresh(todo)

#     return True
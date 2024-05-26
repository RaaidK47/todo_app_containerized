from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, SQLModel, create_engine, Session, select
import psycopg2
import os

from typing import Annotated, Union
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import logging

logging.getLogger('passlib').setLevel(logging.ERROR) # To Suppress bcrypt Warnings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "cb96bd461cb3262adc143a16023c243ce09cae5a6b52db99dc12a8ca128edd0f"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

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


# Get Secret values from you OS Environment
db_name = "todo_db"
db_pass = "oVicMndBI84f"
conn_string = f"postgresql://todo_db_owner:{db_pass}@ep-ancient-bread-a5kwtqzb.us-east-2.aws.neon.tech/{db_name}?sslmode=require"

def createEngineFunction():
    try:
        engine = create_engine(conn_string)
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
def hello():
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

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    print(form_data.username)
    print(form_data.password)
    users_all = fetch_users()
    user = authenticate_user(users_all, form_data.username, form_data.password)
    if not user:
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
    return Token(access_token=access_token, token_type="bearer")

@app.get("/users/me/", response_model=Users)
async def read_users_me(
    current_user: Annotated[Users, Depends(get_current_active_user)],
):
    '''Get Currently Active User'''
    return current_user

@app.get("/users/me/todos/")
def get_todos_user(
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
    return results.all()

@app.post("/users/me/todos/")
def create_todo(current_user: Annotated[Users, Depends(get_current_active_user)],
                todo: ToDos, 
                db: Session = Depends(create_session)
):
    '''Create a New ToDo Item for the
    User that is currently Logged In'''

    print("ToDo Created for User: " + current_user.username)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@app.put("/users/me/todos/{todo_id}")
def update_todo(current_user: Annotated[Users, Depends(get_current_active_user)],
                todo_id: int, 
                updated_todo: ToDos, 
                db: Session = Depends(create_session)):
    
    '''Updating ToDo Item for the User that is
    currently Logged In'''

    statement = select(ToDos).where(ToDos.id == todo_id)
    results = db.exec(statement)
    todo = results.one()

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    if(todo.username == str(current_user.username).lower()):
        todo.title = updated_todo.title
        todo.description = updated_todo.description
        todo.target_date = updated_todo.target_date

        db.add(todo)
        db.commit()
        db.refresh(todo)
        return True

    else:
        print("You are not authorized to updated this ToDos")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not Authorized to Update this ToDo",
        )



@app.patch("/users/me/todos/{todo_id}")
def update_todo_completed(current_user: Annotated[Users, Depends(get_current_active_user)],
                          todo_id: int, todo_updated:ToDos, 
                          db: Session = Depends(create_session)):
    # print(todo_updated)
    '''Updating ToDo Item Completion Status
    for the User that is currently Logged In'''
    statement = select(ToDos).where(ToDos.id == todo_id)
    results = db.exec(statement)
    todo = results.one()

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    if(todo.username == str(current_user.username).lower()):
        todo.completed = todo_updated.completed

        db.add(todo)
        db.commit()
        db.refresh(todo)

        return True
    
    else:
        print("You are not authorized to Update Completion Status this ToDos")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not Authorized to change ToDo",
        )


@app.delete("/users/me/todos/{todo_id}")
def delete_todo(current_user: Annotated[Users, Depends(get_current_active_user)],
                todo_id: int, 
                db: Session = Depends(create_session)):
    '''Deleting ToDo Item for the User that is
    currently Logged In'''

    statement = select(ToDos).where(ToDos.id == todo_id)
    results = db.exec(statement)
    todo = results.one()

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if (todo.username == str(current_user.username).lower()):
        db.delete(todo)
        db.commit()
        return {"message": "Todo deleted successfully"}
    
    else:
        print("You are not authorized to Delete this ToDos")
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
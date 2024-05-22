from sqlmodel import SQLModel   
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, SQLModel, create_engine, Session, select
import psycopg2
import os

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

@app.get("/todos/")
def retrieve_todos(username = ToDos.username, db: Session = Depends(create_session)):
    # print(username)
    statement = select(ToDos).where(ToDos.username == username)
    results = db.exec(statement)
    return results.all()

@app.get("/todos/{todo_id}")
def get_todo_id(todo_id: int, db: Session = Depends(create_session)):
    todo = db.get(ToDos, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, updated_todo: ToDos, db: Session = Depends(create_session)):
    statement = select(ToDos).where(ToDos.id == todo_id)
    results = db.exec(statement)
    todo = results.one()

    todo.title = updated_todo.title
    todo.description = updated_todo.description
    todo.target_date = updated_todo.target_date

    db.add(todo)
    db.commit()
    db.refresh(todo)

    return True

@app.patch("/todos/{todo_id}")
def update_todo_completed(todo_id: int, todo_updated:ToDos, db: Session = Depends(create_session)):
    # print(todo_updated)
    statement = select(ToDos).where(ToDos.id == todo_id)
    results = db.exec(statement)
    todo = results.one()

    todo.completed = todo_updated.completed

    db.add(todo)
    db.commit()
    db.refresh(todo)

    return True

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(create_session)):
    todo = db.get(ToDos, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}

@app.post("/todos/")
def create_todo(todo: ToDos, db: Session = Depends(create_session)):
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo
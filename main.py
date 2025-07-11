
from typing import Annotated
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from post_validation import NewPost
import hashlib
from sqlalchemy.exc import IntegrityError

#new
from login_validation import NewSignup

import logging
import sys

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

from sqlmodel import Field, Session, SQLModel, create_engine, select


description = """
This application recieves and displays blog posts for a blog website.

## Posts

Users will be able to:

* **Create posts**
* **See created posts**

Todo:
* **Search Bar**
* **User login**
"""

templates = Jinja2Templates(directory="templates")

class Post(SQLModel, table = True):
    id: int | None = Field(default = None, primary_key= True)
    title: str = Field(index= True)
    content: str
    date_posted: str

#new
class User(SQLModel, table = True):
    id: int | None = Field(default = None, primary_key= True)
    email: str = Field(unique= True, nullable=False)
    password_hash: str = Field(nullable = False)
    is_admin: bool = Field(default= False)
    
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    add_post("test title", "test content", "test date")
    yield
    SQLModel.metadata.drop_all(engine)

app = FastAPI(
    title = "My Blog",
    description = description,
    summary = "A simple app for making and viewing blog posts",
    version = "0.0.1",
    lifespan= lifespan
    )

@app.get("/", response_class=HTMLResponse)
async def load_blog(request: Request):
    return templates.TemplateResponse("blog.html", {"request": request, "posts": get_posts()})



@app.post("/posts/")
def add_post(post_title: str, post_content: str, post_date: str) -> Post:
    post = Post(title=post_title, content = post_content, date_posted = post_date)

    with Session(engine) as session:
        session.add(post)
        session.commit()
        session.refresh(post)

    return post

@app.get("/posts/")
def get_posts() -> list[Post]:
    with Session(engine) as session:
        posts = session.exec(select(Post).offset(0).limit(100)).all()

    return posts

@app.get("/form")
def new_post(request: Request): 
    return templates.TemplateResponse("form.html", {"request" : request})

@app.post("/form")
async def new_post(request: Request):
    form = NewPost(request)
    await form.load_data()
    if form.valid_input():
        post = form.__dict__
        add_post(post["post_title"], post["post_content"], post["post_date"])
        return RedirectResponse(request.url_for('load_blog'), status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("form.html", form.__dict__)

@app.get("/search/")
def search_post(request: Request, query = None):
    with Session(engine) as session:
        posts = search_post(query, session)
        return templates.TemplateResponse("blog.html", {"request": request, "posts": posts})

def search_post(query: str, session: Session):
    posts = session.exec(select(Post).where(Post.title.contains(query)))
    return posts

#new
@app.get("/signup/")
def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

#new
@app.post("/signup/")
async def signup(request: Request):
    signup = NewSignup(request)
    await signup.load_data()
    if await signup.valid_input():
        try:
            user = create_user(signup.email, signup.password)
            return RedirectResponse("blog.html", status_code=status.HTTP_302_FOUND)
        except IntegrityError:
            signup.__dict__.get("errors").append("An account with this email already exists")

            return templates.TemplateResponse("signup.html", signup.__dict__)
        
    return templates.TemplateResponse("signup.html", signup.__dict__)

#new
def create_user(new_email : str, new_password : str):

    hasher = hashlib.sha256()
    hasher.update(new_password)
    hashed = hasher.hexdigest()

    user = User(
        email = new_email,
        password_hash = hashed
    )

    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
    
    return user

app.mount("/static", StaticFiles(directory="static"), name="static")



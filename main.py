
from typing import Annotated
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from post_validation import NewPost


from sqlmodel import Field, Session, SQLModel, create_engine, select


templates = Jinja2Templates(directory="templates")

class Post(SQLModel, table = True):
    id: int | None = Field(default = None, primary_key= True)
    title: str = Field(index= True)
    content: str
    date_posted: str
    
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

app = FastAPI(lifespan= lifespan)

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


app.mount("/static", StaticFiles(directory="static"), name="static")



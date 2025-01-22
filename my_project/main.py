
from fastapi import FastAPI, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from sqlmodel import Field, Session, SQLModel, create_engine, select



app = FastAPI()
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

post_database = [{
    'title': 'First post on my blog',
    'content': 'Welcome to my blog! This is my first post!',
    'date_posted': '10/01/2025'
},{
    'title': 'Second post on my blog',
    'content': 'This is the second post im making on my new blog!',
    'date_posted': '12/01/2025'
},{
    'title': 'Third post on my blog',
    'content': 'This is the third post on my blog',
    'date_posted': '15/01/2025'
}]

@app.get("/", response_class=HTMLResponse)
async def load_blog(request: Request):
    return templates.TemplateResponse("blog.html", {"request": request, "posts": post_database})

#@app.get("/otherpage")
#async def load_other_page(request: Request): 
#    return templates.TemplateResponse("otherpage.html", {"request" : request})


app.mount("/static", StaticFiles(directory="static"), name="static")
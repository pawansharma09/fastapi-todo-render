from fastapi import FastAPI, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app import models, schemas, auth
from app.database import engine, get_db
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-change-in-prod")
ALGORITHM = "HS256"

def get_current_user_from_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    user = db.query(models.User).filter(models.User.email == email).first()
    return user

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    user = get_current_user_from_token(token, db)
    return user

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user:
        return RedirectResponse(url="/todos", status_code=303)
    return RedirectResponse(url="/login", status_code=303)

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.email == email).first()
    if db_user:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Email already registered"
        })
    hashed_pw = auth.get_password_hash(password)
    new_user = models.User(email=email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    return RedirectResponse("/login?registered=true", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    registered = request.query_params.get("registered")
    return templates.TemplateResponse("login.html", {
        "request": request,
        "registered": registered
    })

@app.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid email or password"
        })
    access_token = auth.create_access_token(data={"sub": user.email})
    response = RedirectResponse("/todos", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("access_token")
    return response

@app.get("/todos", response_class=HTMLResponse)
async def todo_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=303)
    todos = db.query(models.Todo).filter(models.Todo.owner_id == user.id).all()
    return templates.TemplateResponse("todos.html", {
        "request": request,
        "user": user,
        "todos": todos
    })

@app.post("/todos")
async def create_todo(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    todo = models.Todo(title=title, description=description, owner_id=user.id)
    db.add(todo)
    db.commit()
    return RedirectResponse("/todos", status_code=303)

@app.post("/todos/{todo_id}/toggle")
async def toggle_todo(todo_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.owner_id == user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    todo.completed = not todo.completed
    db.commit()
    return RedirectResponse("/todos", status_code=303)

@app.post("/todos/{todo_id}/delete")
async def delete_todo(todo_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.owner_id == user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return RedirectResponse("/todos", status_code=303)
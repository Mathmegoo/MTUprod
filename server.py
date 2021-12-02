import os
from fastapi import Depends
from sqlalchemy.orm.session import Session
from starlette.responses import HTMLResponse
from models.database import SQLALCHEMY_DATABASE_URL, engine, create_db, SessionLocal
from fastapi import FastAPI, Form, Cookie , Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, Response
from typing import Optional
import uvicorn
import hmac
import hashlib
import base64
import json
from models import models 
from models import crud



app = FastAPI()

templates = Jinja2Templates(directory='templates')

SECRET_KEY = "8c680338db222af993a2a80fe2e1b269911ca701f1d5c7ec29dafb1dff3e1b9b"
PASSWORD_SALT = "d43955a5688a5f61688efd38cec0e97ce499e038163b994bcbaf13b938a6fd73"
#create session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def sign_data(data: str) -> str:
    """Подписывает данные data"""
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest().upper() 

def get_username_from_signed_string(username_signed: str) -> Optional[str]:
    username_base64, sign = username_signed.split(".")
    username = base64.b64decode(username_base64.encode()).decode()
    valid_sign = sign_data(username)
    if hmac.compare_digest(valid_sign, sign):
        return username


def verify_password(password:str, password_hash: str) -> bool:
    return hashlib.sha256( (password + PASSWORD_SALT).encode()).hexdigest().lower() == \
    password_hash.lower()

def hash_password(password: str) -> str:
    return hashlib.sha256( (password + PASSWORD_SALT).encode()).hexdigest().lower()





    

    



users = {
    'nikita@user.com': {
        'name': 'Nikita',
        'password' : 'c1785c67a51071c144222ded7eceddb12f7e5334445c38ff8a05dc333ca50fdb',
        'balance': 200_000,
    },
    'petr@user.com': {
        'name': 'Petr',
        'password': 'e9fc03401c29d6b48ddf5878156a2ea7cc026db62d77931c7f1b32a107174a1b',
        'balance': 10_000
    }
}


@app.get('/admin', response_class=HTMLResponse)#Доделать вдминский роут для публткации статей!
def admin_page (request : Request, username : Optional[str] = Cookie(default=None),  db : Session = Depends(get_db), ):
    valid_user = get_username_from_signed_string(username)
    if valid_user == "nikita@username.com":
        
        vie_posts = db.query(models.Articles).all()
        vie_comments = db.query(models.Comments).all()
        responce = templates.TemplateResponse('admin.html', {"request" : request, "posts" : vie_posts, "comments" :vie_comments})
        return responce
    else:
        return Response(
            json.dumps({
                'success' : True,
                'message' : f"Hello, you not admin("
            }), 
            media_type='application/json'
            )



@app.post('/admin', response_class=HTMLResponse)#Доделать вдминский роут для публткации статей!
def admin_page (request : Request, username : Optional[str] = Cookie(default=None), title: str = Form(...), content : str = Form(...), db : Session = Depends(get_db), ):
    valid_username = get_username_from_signed_string(username)
    if valid_username == "nikita@username.com":
        crud.create_article(title, content, db)
        vie_posts = db.query(models.Articles).all()
        vie_comments = db.query(models.Comments).all()
        responce = templates.TemplateResponse('admin.html', {"request" : request, "posts" : vie_posts, "comments" :vie_comments})
        return responce
    else:
        return Response(
            json.dumps({
                'success' : True,
                'message' : f"Hello, you not admin("
            }), 
            media_type='application/json'
            )




@app.get('/', response_class=HTMLResponse)
def index_page(request : Request, username : Optional[str] = Cookie(default=None), db : Session = Depends(get_db)):
    with open('templates/login.html', 'r') as f:
        login_page = f.read()
    

    if not username :
        return Response(login_page, media_type='text/html')
    
        
        
    valid_username = get_username_from_signed_string(username)
    if not valid_username:
        responce = Response(login_page, media_type='text/html')
        responce.delete_cookie(key="username")
        return responce
    try:
            user = crud.get_user_by_login(valid_username,db)  
    except KeyError:
            responce = Response(login_page, media_type = 'text/html')
            responce.delete_cookie(key="username")
            return responce
    
    
    vie_posts = db.query(models.Articles).all()
    vie_comments = db.query(models.Comments).all()
    responce = templates.TemplateResponse('home.html', {"request" : request, "posts" : vie_posts, "comments" :vie_comments})
    return responce
     


@app.post('/', response_class=HTMLResponse, )
def post_articles_and_comm(request : Request, username : Optional[str] = Cookie(default=None) ,article_id : str = Form(...), content : str = Form(...), db : Session = Depends(get_db), ):
    valid_username = get_username_from_signed_string(username)
    crud.create_comment(valid_username,article_id, content, db)
    vie_posts = db.query(models.Articles).all()
    vie_comments = db.query(models.Comments).all()
    responce = templates.TemplateResponse('home.html', {"request" : request, "posts" : vie_posts, "comments" :vie_comments})
    return responce







@app.post('/login',   )
def process_login_page(username : str = Form(...), password : str = Form(...), db = Depends(get_db)):
    
    verified_user = crud.get_user_by_login(username, db)
    print (verified_user)
    if not verified_user or not verify_password(password, verified_user.passwordu):

        
        return Response(
            json.dumps({
                'success' : False,
                'message' : "I don't know you!" 
            }), 
            media_type='application/json'
            )
    print(username)
    responce = Response(
            json.dumps({
                'success' : True,
                'message' : f"Hello, {verified_user.nickname}!" 
            }), 
            media_type='application/json'
            )
        

    username_signed = base64.b64encode(username.encode()).decode() + '.' + sign_data(username)
    
    responce.set_cookie(key="username", value=username_signed)
    return responce


# route регистрации 
@app.get('/reg')
def registration_func():
    with open('templates/reg.html', 'r') as f:
        reg_page = f.read()
    return Response(reg_page, media_type='text.html')

@app.post('/reg')
def process_login_page(username : str = Form(...), nickname : str =Form(...), password1 : str = Form(...),\
    password2 : str = Form(...), db: Session = Depends(get_db)):
    if password1 == password2:
        successful = crud.create_user(username,nickname,password1,db)

    if successful:
       responce = Response(
        json.dumps({
            'success' : True,
            'message' : f"Hello, { username}"
        }),
        media_type='application/json')
    return responce 








if __name__ == "__main__":
    uvicorn.run("server:app", port=8000, host= "127.0.0.1", reload=True)
    db_is_created = os.path.exists(SQLALCHEMY_DATABASE_URL)
    if not db_is_created:
        create_db()


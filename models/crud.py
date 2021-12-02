from sqlalchemy.orm import Session, query
from sqlalchemy.sql.operators import exists
from server import verify_password, get_db, hash_password
from . import models 
from fastapi import Depends

def get_user_by_id( user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Site_users).filter(models.Site_users.id == user_id).first()


def get_user_by_nickname( nickname: str, db: Session ):
    return db.query(models.Site_users).filter(models.Site_users.nickname == nickname).first()

def get_user_by_login( login: str, db: Session ):
    return db.query(models.Site_users).filter(models.Site_users.login == login).first()

def get_users(db: Session, skip: int = 0, limit: int = 500, ):
    return db.query(models.Site_users).offset(skip).limit(limit).all()

def create_user( login, nickname, password, db: Session ):
    db_user = models.Site_users(login=login, nickname= nickname, passwordu = hash_password(password))
    print(db)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_articles ( db:Session, skip: int = 0, limit: int = 500,):
    exsist_articles = db.query(models.Articles).offset(skip).limit(limit).all()
    return exsist_articles

def create_article( title, content, db: Session ):
    db_article = models.Articles(title=title, content= content, )
    print(db)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

def get_comments ( db:Session, skip: int = 0, limit: int = 5000,):
    exsist_comments = db.query(models.Comments).offset(skip).limit(limit).all()
    return exsist_comments

def create_comment( valid_username, article_id, content, db: Session ):
    autor = get_user_by_login(valid_username, db)
    autor_id = autor.id
    db_comment = models.Comments(autor_id=autor_id,article_id = article_id, content= content, )
    print(db)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

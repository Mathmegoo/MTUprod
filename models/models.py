from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date
from datetime import date
from models.database import Base
from sqlalchemy.orm import relationship


class Site_users(Base):
    __tablename__ = 'site_users'

    id = Column(Integer, unique=True, primary_key=True, nullable=False, autoincrement=True)
    login = Column(String, unique=True, nullable=False)
    nickname = Column(String, unique=True, nullable=False)
    passwordu = Column(String, nullable=False)
    

    def __repr__(self) -> str:
        info: str = f'Site_user [ID: {self.id}, login: {self.login}, nickname: {self.nickname}, \
        passwordu: {self.passwordu},] '
        return info

# модели из фласка, нуждаются в адаптации
class Articles(Base):
    __tablename__ = 'articles'
    id = Column (Integer, primary_key=True, autoincrement=True)
    title = Column (String(200), unique=True, nullable=False)
    content = Column (String(5000), nullable=False)
    date_created = Column (Date, default=date.today)
    is_visible = Column (Boolean, default=True, nullable=False)

class Comments (Base):
    __tablename__ = 'comments'
    id = Column (Integer, primary_key=True, autoincrement=True)
    autor_id = Column(
        Integer,
        ForeignKey('site_users.id'),
        nullable=False,
        index=True
        )

    autor = relationship('Site_users', foreign_keys=[autor_id,])
    article_id = Column(
        Integer,
        ForeignKey('articles.id'),
            nullable=False,
            index=True
    )
    
    content = Column (String(400), nullable=False)
    is_visible = Column (Boolean, default=True, nullable=False)
    def __str__(self):
        content = self.content
        autor = self.autor.nickname
        return f'{autor} comment: {content}' 

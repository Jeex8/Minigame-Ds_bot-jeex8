import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):#Код ячеек бд
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    gaymer = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    opponent = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    stage = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    pole = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    server_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    channel_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

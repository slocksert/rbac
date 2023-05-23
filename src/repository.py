import models
from database import engine

from sqlmodel import Session, select
from passlib.context import CryptContext
from decouple import config
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from jose import JWTError, jwt
import re

session = Session(bind=engine)

SECRET_KEY = config('SECRET_KEY')
ALGORITHM = config('ALGORITHM')

crypt_context = CryptContext(schemes=["argon2"]) #Argon2 abstraction

#Create roles directly in the db
#This function is called in the migration
def create_roles():
    
    adm_role = models.Roles(name="admin")
    normal_role = models.Roles(name="normal_user")

    session.add_all([adm_role, normal_role])
    session.commit()

#Create the default admin user in the db
def create_admin():
    
    query = select(models.Roles).where(models.Roles.name == "admin")
    role_admin = session.exec(query).first()

    admin = models.Users(
        username="admin", email="admin@admin", password=crypt_context.hash("admin"), role_id=role_admin.id
    )

    session.add(admin)
    session.commit()

#Email validator using regular expressions 
def email_is_valid(email: str) -> bool:
    regex = r'\b[A-Za-z0-9._%+-]+@[A-za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    if re.fullmatch(regex, email):
        return True
    return False

# Class that contains all the functions called by the routes
class AuthUser:

    def __init__(self) -> None:
        self.session = session

    def user_register(self, user: models.Users):
        new_user = models.Users(
            username=user.username, password=crypt_context.hash(user.password), email=user.email
        )

        user_query = select(models.Users).where(models.Users.username == user.username)
        username = self.session.exec(user_query).first()

        email_query = select(models.Users).where(models.Users.email == user.email)
        email = self.session.exec(email_query).first()

        if username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Existent user"
            )
        
        if not email_is_valid(user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format"
            )
        
        if email:
            raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Existent email"
        )

        self.session.add(new_user)
        self.session.commit()

    def user_login(self, user: models.Users, expires_in: int = 30):
        user_query = select(models.Users).where(models.Users.username == user.username)
        username = self.session.exec(user_query).first()

        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorret username or password"
            )
        
        if not crypt_context.verify(user.password, username.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorret username or password"
            )

        exp = datetime.utcnow() + timedelta(minutes=expires_in)
        payload = {
            "sub": user.username,
            "exp": exp
        }

        access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return {
            "access_token": access_token,
            "exp": exp.isoformat()
        }

    def verify_token(self, access_token):
        try:
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            sub = payload["sub"]
            #Query that search for the user by decoding the access_token
            username_query = select(models.Users).where(models.Users.username == sub)
            username = session.exec(username_query).first()
            

            if username is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
            
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    def verify_admin(self, access_token):
        try:
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload["sub"] == "admin":
                return
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized", headers={"WWW-Authenticate": "Bearer"})

        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")
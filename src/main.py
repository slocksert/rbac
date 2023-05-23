from routes import register, login, index, adm_route

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from decouple import config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(register)
app.include_router(login)
app.include_router(index)
app.include_router(adm_route)

if __name__ == "__main__": #Starts the API when main.py is executed
    uvicorn.run(
        "main:app",
        host=config("host"),
        port=8000,
        reload=1,
        server_header=0
    )
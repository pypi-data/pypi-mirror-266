from fastapi import FastAPI
from routes.read import read_router
from routes.write import write_router

app = FastAPI()
app.include_router(read_router)
app.include_router(write_router)

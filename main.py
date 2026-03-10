from fastapi import FastAPI
from routers import auth, vacancies  

app = FastAPI(title="Tap.im API", version="1.0")

app.include_router(auth.router)
app.include_router(vacancies.router) 

@app.get("/")
def root():
    return {"message": "Application is running!"}
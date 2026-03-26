from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from routers import auth, vacancies, chat, profiles , favorites


app = FastAPI(title="Tap.im API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(vacancies.router) 
app.include_router(chat.router)
app.include_router(profiles.router)
app.include_router(favorites.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # разные сообщения для разных роутов
    if "/auth/" in request.url.path:
        return JSONResponse(status_code=422, content={"detail": "Invalid email or password"})
    
    # для остальных роутов показываем реальную ошибку
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.get("/")
def root():
    return {"message": "Application is running!"}
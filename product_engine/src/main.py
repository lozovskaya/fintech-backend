from fastapi import FastAPI
from src.models import database
from src.routers import product_router, agreement_router

database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.include_router(product_router.router)
app.include_router(agreement_router.router)

@app.get("/")
async def root():
    return {"message": "Hello World!"}
from fastapi import FastAPI
from routers import scoring_router


app = FastAPI()


app.include_router(scoring_router.router)

@app.get("/", summary="A welcome message", description="Gets the name of the service")
async def root():
    return {"message": "Scoring Origination"}
from fastapi import FastAPI, HTTPException
import requests

from dependencies import PRODUCT_ENGINE_URL, ORIGINATION_URL
from models.schemas import AgreementRequest, ApplicationRequest


app = FastAPI()

@app.get("/", summary="A welcome message", description="Gets the name of the service.")
async def root():
    return {"message": "Gateway service"}


@app.get("/product", summary="Get all products", description="Fetches a list of all products from the Product Engine service.")
async def get_products():
    response = requests.get(f"{PRODUCT_ENGINE_URL}/product")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@app.get("/product/{product_code}", summary="Get product by internal code", description="Fetches a product by its code from the Product Engine service.")
async def get_product_by_code(product_code: str):
    response = requests.get(f"{PRODUCT_ENGINE_URL}/product/{product_code}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@app.post("/agreement", summary="Create agreement", description="Creates a new agreement in the Product Engine service.")
async def create_agreement(agreement: AgreementRequest):
    response = requests.post(f"{PRODUCT_ENGINE_URL}/agreement", json=agreement.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@app.post("/application", summary="Create application", description="Creates a new application in the Origination service.")
async def create_application(application: ApplicationRequest):
    response = requests.post(f"{ORIGINATION_URL}/application", json=application.model_dump())
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


@app.post("/application/{application_id}/close", summary="Close application", description="Closes an application in the Origination service.")
async def close_application(application_id: str):
    response = requests.post(f"{ORIGINATION_URL}/application/{application_id}/close")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()
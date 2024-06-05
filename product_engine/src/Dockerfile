FROM python:3.10

WORKDIR /app

RUN pip install --upgrade pip
ADD ./product_engine/src/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

ADD ./product_engine/src /app
ADD ./common/ /app/common

EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "5"]

FROM python:3.10

ADD ./product_engine/src /app
ADD ./common/ /app/common
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

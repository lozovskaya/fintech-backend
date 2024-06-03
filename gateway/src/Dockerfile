FROM python:3.10

ADD ./gateway/src /app
ADD ./common/ /app/common
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 7022
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7022"]

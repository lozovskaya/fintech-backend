FROM python:3.10


WORKDIR /app

RUN pip install --upgrade pip
ADD ./scoring/src/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

ADD ./scoring/src /app
ADD ./common/ /app/common

EXPOSE 8008
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8008", "--workers", "5"]

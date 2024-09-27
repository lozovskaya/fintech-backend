FROM python:3.10

WORKDIR /app

RUN pip install --upgrade pip
ADD ./origination/src/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

ADD ./origination/src /app
ADD ./common/ /app/common

EXPOSE 90
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "90", "--workers", "5"]
FROM python:3.10

WORKDIR /app
COPY ./requirements.txt ./requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
EXPOSE 7022
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7022"]

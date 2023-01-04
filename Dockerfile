FROM python:3.11-slim-buster



COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app

CMD [ "python3", "/app/main.py"] 
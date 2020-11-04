FROM docker.io/library/python:3.8

COPY . .

RUN pip install -r requirements.txt

EXPOSE 443

CMD python -u mutation.py

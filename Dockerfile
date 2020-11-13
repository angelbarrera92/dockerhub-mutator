FROM docker.io/library/python:3.9

COPY . .

RUN pip install -r requirements.txt

EXPOSE 443

CMD python -u mutation.py

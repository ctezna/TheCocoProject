FROM python:3.6-alpine

RUN adduser -D cocoproject_web

WORKDIR /home/cocoproject_web

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt


COPY cocoProject cocoProject
COPY migrations migrations
COPY config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP cocoProject

RUN chown -R cocoproject_web:cocoproject_web ./
USER cocoproject_web

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]


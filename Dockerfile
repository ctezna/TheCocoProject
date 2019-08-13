FROM python:3.6-alpine
RUN ln -s /usr/lib/x86_64-linux-gnu/libz.so /lib/
RUN ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /lib/

RUN adduser -D cocoproject_web

WORKDIR /home/cocoproject_web

COPY requirements.txt requirements.txt
RUN apk add --no-cache --update python3-dev  gcc build-base
RUN apk add zlib-dev libjpeg-turbo-dev

RUN apk add postgresql-dev
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
CMD ["./boot.sh"]


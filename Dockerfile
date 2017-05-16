FROM python:3.6-alpine

MAINTAINER Derek M. Frank <derek at frank dot sh>

WORKDIR /code

COPY . /code

RUN pip install -r requirements.txt

CMD ["nohup", "/code/run.sh"]

SHELL := /usr/bin/env zsh

all: clean

clean:
	find . -not \( -path "*/.git" -prune \) -name "*.py{c,o}" -or -path "*/__pycache__" -exec rm -r {} + ;
	: > {nohup.out,bot.log}

lint:
	pylint simple slackbot.py

stop:
	docker-compose stop

restart: stop clean
	docker-compose restart

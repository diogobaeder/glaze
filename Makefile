export TESTING=1

build: test lint

test:
	python manage.py test

lint:
	flake8 .

migrations:
	python manage.py makemigrations

resetdb:
	rm -f db.sqlite3
	python manage.py migrate
	python manage.py loaddata users.json

run:
	python manage.py runserver

setup:
	pip install -r requirements.txt
	python manage.py makemigrations thumbnail

freeze:
	pip freeze > requirements.txt

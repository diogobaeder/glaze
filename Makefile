export TESTING=1

build: test lint

test:
	python manage.py test

lint:
	flake8 .

migrations:
	python manage.py makemigrations

apply-migrations:
	python manage.py migrate

delete-migrations:
	find . -type f -regex '.*/migrations/[0-9].*\.py' -delete

reset-db:
	rm -f db.sqlite3
	python manage.py migrate
	python manage.py loaddata users.json

reset-migrations: delete-migrations migrations

run:
	python manage.py runserver

setup:
	pip install -r requirements.txt
	python manage.py makemigrations thumbnail

freeze:
	pip freeze > requirements.txt

messages:
	python manage.py makemessages -a
	python manage.py compilemessages

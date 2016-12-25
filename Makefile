build: test

test:
	python manage.py test

migrations:
	python manage.py makemigrations

resetdb:
	rm -f db.sqlite3
	python manage.py migrate

run:
	python manage.py runserver

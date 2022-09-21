rm demo.db
source demo/setup.sh
poetry run python manage.py createsuperuser

#!/bin/sh

echo "Apply database migrations"
python manage.py migrate

if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    echo "Create Super User"
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
fi

exec "$@"

python app/manage.py migrate
python app/manage.py collectstatic --noinput
python app/manage.py createsuperuser_custom
#python app/manage.py runserver 0.0.0.0:8000
# shellcheck disable=SC2164
cd app
gunicorn project.wsgi:application --bind 0.0.0.0:8000 \
    --access-logfile /app/logs/gunicorn_access.log \
    --error-logfile /app/logs/gunicorn_error.log

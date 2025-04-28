pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn instafi_agents.wsgi:application --bind=0.0.0.0:$PORT
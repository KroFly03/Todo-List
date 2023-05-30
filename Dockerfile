FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --no-cache -r requirements.txt

COPY . .

EXPOSE 8000

CMD python manage.py runserver 0.0.0.0:8000

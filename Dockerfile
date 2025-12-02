FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Créer les applications Django si elles n'existent pas
RUN if [ ! -d "messageries" ]; then django-admin startapp messageries; fi
RUN if [ ! -d "litige" ]; then django-admin startapp litige; fi

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

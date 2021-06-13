FROM python:3.9.0-slim


RUN pip install pipenv

# Install dependencies
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install --deploy --system
RUN pip install gunicorn==19.9.0

COPY ./services/api/ /api/
WORKDIR /

EXPOSE 5000
ENV PYTHONPATH "${PYTHONPATH}:/api"

CMD ["gunicorn", "-c", "api/gunicorn.ini", "api.wsgi:app"]

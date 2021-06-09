FROM python:3.7

ENV PIP_NO_CACHE_DIR=false
RUN pip install pipenv
WORKDIR /opt
COPY ./Pipfile ./
RUN pipenv install --skip-lock --sequential
COPY ./src /opt/app/
WORKDIR /opt/app
EXPOSE 8080
CMD ["pipenv", "run", "python", "start.py"]

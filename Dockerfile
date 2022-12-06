FROM python:3.8
LABEL maintainer="Alex Barraza <alex.barraza@computacenter.com>"

WORKDIR /app

COPY src/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src .

EXPOSE 8000

CMD [ "python", "./main.py" ]
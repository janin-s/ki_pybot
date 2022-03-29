FROM python:3.10.4-alpine3.15
# FROM python:3.10

WORKDIR /usr/src/app

# to get gcc and zlib and jpeg to make matplotlib work
RUN apk add build-base zlib-dev jpeg-dev
ENV LIBRARY_PATH=/lib:/usr/lib

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install wheel
RUN pip install --no-cache-dir -r requirements.txt
RUN pip list

RUN python -c "import sqlite3; print(sqlite3.sqlite_version)"

COPY . .

CMD [ "python", "./launcher.py" ]
FROM python:3.10.4-alpine3.15
# FROM python:3.10

WORKDIR /usr/src/app

# to get gcc for compiling libs and zlib and jpeg to make matplotlib work
RUN apk add build-base zlib-dev jpeg-dev

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install wheel
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./launcher.py" ]
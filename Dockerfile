FROM python:alpine

WORKDIR /usr/src/app

ADD main.py .
COPY requirements.txt ./

RUN apk add --no-cache ffmpeg
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]
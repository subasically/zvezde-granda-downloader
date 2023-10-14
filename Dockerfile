FROM python:alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY main.py ./

RUN apk add --no-cache ffmpeg
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]
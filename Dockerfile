FROM python:3.10.2-bullseye

RUN apt-get update -y
RUN apt-get upgrade -y
RUN pip install pip -U

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt -U

COPY . .
COPY data/docker/config.py .

CMD ["python", "main.py", "--main"]
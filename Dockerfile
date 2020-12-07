FROM python:3.8-slim

RUN pip3 install numpy matplotlib scipy seaborn

COPY . /app

WORKDIR /app

CMD ["python3", "-u", "main.py"]

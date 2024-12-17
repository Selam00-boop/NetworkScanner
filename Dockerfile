FROM python:3.9

WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y iputils-ping
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "utility.py"]
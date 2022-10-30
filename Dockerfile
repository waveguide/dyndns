FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir pip --upgrade
RUN pip install --no-cache-dir -r requirements.txt

COPY dyndns.py .

ENTRYPOINT ["python", "dyndns.py"]

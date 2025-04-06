FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "5000", "--server.headless", "true"]
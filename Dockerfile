FROM python:3.12

WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt 

# COPY codes
COPY ./ /app

ENV PYTHONPATH=/app

CMD ["uvicorn", "bot:app", "--host", "0.0.0.0", "--port", "8080"]
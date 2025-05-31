FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt --no-cache-dir
CMD ["python", "main.py"]
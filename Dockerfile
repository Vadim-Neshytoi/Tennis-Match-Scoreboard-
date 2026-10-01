FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV HOST=0.0.0.0
ENV PORT=8080
ENV STATIC_ROOT=/app/static
ENV TEMPLATE_DIR=/app/templates

EXPOSE 8080

CMD ["python", "main.py"]
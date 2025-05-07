FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create output directory
RUN mkdir -p output
RUN mkdir -p static/images

# Expose port for the Flask application
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]

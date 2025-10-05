FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY backend/prediction /app/prediction
COPY backend/data /app/data
COPY backend/api_server.py /app/api_server.py

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "api_server.py"]

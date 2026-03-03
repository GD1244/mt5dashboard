FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the backend code
COPY backend/ ./backend/

WORKDIR /app/backend

# Expose port
EXPOSE 8080

# Run the server
CMD ["python", "server.py"]
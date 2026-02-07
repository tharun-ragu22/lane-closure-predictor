# Use the official lightweight Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Run the web service on container startup
# We use uvicorn directly to ensure it handles the Cloud Run port correctly
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
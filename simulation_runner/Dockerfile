# Use a lightweight Python image
FROM python:3.12-slim

# Install SUMO and dependencies
# we use -y to skip confirmation prompts during build
RUN apt-get update && apt-get install -y sumo sumo-tools sumo-doc libgl1 libglx-mesa0 libx11-6 && rm -rf /var/lib/apt/lists/*

# Set the mandatory environment variable for TraCI
ENV SUMO_HOME=/usr/share/sumo

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the simulation files
COPY . .

# Set the command to run your script
# Using python3 instead of py for the Linux container
CMD ["python3", "main.py"]
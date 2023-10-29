# Use the official Python 3.11-slim image as the base image
FROM python:3.11-slim

# Set the working directory within the container to /app
WORKDIR /app

# Copy the application code from the host machine to the container's /app directory
COPY . /app

# Install the Python dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000, allowing external connections to this port
EXPOSE 5000

# Define the command to run when the container starts
CMD python main.py

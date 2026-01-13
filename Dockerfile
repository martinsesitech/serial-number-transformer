# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy the Python script
COPY serial_transformer.py .

# Run the interactive CLI
CMD ["python", "serial_transformer.py"]
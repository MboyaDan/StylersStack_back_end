# Use the official Python image.
FROM python:3.10-slim

# Set the working directory inside the container.
WORKDIR /app

# Copy only requirements first for caching layers.
COPY requirements.txt .

# Install dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container.
COPY . .

# Expose port 8000 for FastAPI
EXPOSE 8000

# Command to run the FastAPI app with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

ENV PYTHONPATH=/app

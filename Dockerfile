# Use the official Python image from the Docker Hub
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files into the container
COPY pyproject.toml poetry.lock ./

# Install Poetry
RUN pip install --no-cache-dir poetry

# Install dependencies
RUN poetry install

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000
# Command to run the application
CMD ["sh", "-c", "poetry run alembic upgrade head && poetry run uvicorn main:app --host 0.0.0.0 --port 8000"]

# Project Description

This project is my personal developed application aimed at showcasing my programming and web development skills. It is built using Python, FastAPI, and Celery, creating an efficient and scalable system for managing user contacts. PostgreSQL is used for data storage, Redis serves as a message broker for asynchronous tasks, and Docker for application containerization.

## Functionality

- **User Authentication and Authorization:** Allows users to securely register, log in, and manage their accounts with JWT token-based authentication.
  
- **Contact Management:** Provides CRUD operations for managing contacts, including adding, editing, and deleting contacts. Users can establish relationships between contacts.

- **Asynchronous Tasks:** Utilizes Celery and Redis for executing background tasks asynchronously, enhancing the responsiveness of the application.

- **Data Security:** Ensures data security with encrypted password storage using bcrypt hashing, protecting user credentials.

## Technologies and Tools

Python, FastAPI, SQLAlchemy, PostgreSQL, Redis, Celery, Docker, Poetry.

## Available Commands

- `docker-compose up --build`: Start the application with PostgreSQL database and Redis.
  
- `poetry install`: Install Python dependencies using Poetry.
  
- `poetry run alembic upgrade head`: Perform database migrations using Alembic.
  
- `poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload`: Launch the FastAPI server for the application.

## Contributions and Acknowledgements

I am thankful to GoIT and the web development community for their support and inspiration throughout the creation of this project.

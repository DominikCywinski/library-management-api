# Library Management System API

This is a simple API for managing books in a library. It allows employees to track and update the status of books, 
including adding, deleting, and updating the availability of books.

## Features

- **Add a new book** to the library
- **Get a list of all books** in the library
- **Delete a book** from the library by serial number
- **Update the status** of a book
- **Custom Logging** of actions

## Technologies

- **FastAPI** – Python framework for building APIs
- **PostgreSQL** – Database for storing book information
- **SQLAlchemy** – ORM (Object-Relational Mapper) for interacting with a PostgreSQL database
- **Pydantic** – Data validation and serialization/deserialization in the API
- **Docker** – Containerization
- **Docker Compose** – Managing multiple services (application and database)

## Installation
### Requirements

- Docker
- Docker Compose

### Steps
1. Clone the repository:

    ```bash
    git clone https://github.com/DominikCywinski/library-management-api
    cd library-management-api
    ```

2. Create and start the containers using Docker Compose:

    ```bash
    docker compose up
    ```

3. The application will be running at `http://localhost:8000`. You can interact with the API using `http://localhost:8000/docs`

## Testing
To run the tests, run the following command:

```bash
docker compose exec api pytest tests/ -v
```
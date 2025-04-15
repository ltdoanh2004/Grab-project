# Skeleton Bootcamp Backend

A modern RESTful API for managing todos efficiently, built with Go using clean architecture principles.

## Tech Stack

- Go 1.21
- Gin v1.10.0 (Web Framework)
- GORM v1.25.7 (ORM)
- MySQL (Database)
- Uber FX v1.20.1 (Dependency Injection)
- Viper v1.18.2 (Configuration Management)
- Zerolog v1.32.0 (Logging)
- Swagger v1.16.3 (API Documentation)

## Project Structure

```
.
├── cmd
│   └── main.go           # Application entry point
├── config
│   └── config.go         # Configuration management
├── database
│   └── db.go            # Database connection setup
├── internal
│   ├── controller       # HTTP handlers
│   ├── dto             # Data Transfer Objects
│   ├── logger          # Logging configuration
│   ├── model           # Data models
│   ├── repository      # Database operations
│   └── service         # Business logic
├── docs                # Swagger documentation
├── docker-compose.yml  # Docker compose configuration
├── Dockerfile         # Docker build configuration
├── go.mod            # Go module file
├── go.sum            # Go module checksums
└── README.md         # Project documentation
```

## Getting Started

### Prerequisites

- Go 1.21 or higher
- Docker and Docker Compose
- MySQL (if running locally)

### Running with Docker

1. Clone the repository:
```bash
git clone https://github.com/tuannguyensn2001/skeleton-bootcamp-backend
cd skeleton-bootcamp-backend
```

2. Start the application using Docker Compose:
```bash
docker-compose up -d
```

The application will be available at `http://localhost:8080`

### Running Locally

1. Clone the repository
2. Create a `.env` file based on `.env.example`:
```env
SERVER_PORT=8080
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=password
DATABASE_NAME=todo_db
```

3. Run MySQL database (or use Docker Compose for database only)
4. Run the application:
```bash
go run cmd/main.go
```

## API Endpoints

### Health Check
- `GET /health` - Check API health status

### Todo Endpoints

- `GET /api/v1/todos` - Get all todos
- `GET /api/v1/todos/:id` - Get a specific todo
- `POST /api/v1/todos` - Create a new todo
- `PUT /api/v1/todos/:id` - Update a todo
- `DELETE /api/v1/todos/:id` - Delete a todo

## Request/Response Examples

### Create Todo
```json
POST /api/v1/todos
{
    "title": "Complete project",
    "description": "Finish the todo app",
    "status": "pending"
}
```

### Response Format
```json
{
    "message": "Todo created successfully",
    "data": {
        "id": 1,
        "title": "Complete project",
        "description": "Finish the todo app",
        "status": "pending",
        "created_at": "2024-03-12T10:00:00Z",
        "updated_at": "2024-03-12T10:00:00Z"
    }
}
```

## API Documentation

### Swagger

The API is documented using Swagger/OpenAPI. To access the documentation:

1. Install Swagger tools:
```bash
go install github.com/swaggo/swag/cmd/swag@latest
```

2. Generate Swagger documentation:
```bash
swag init -g cmd/main.go
```

3. Access the Swagger UI:
   - Start the application
   - Visit `http://localhost:8080/swagger/index.html`

The Swagger UI provides interactive documentation where you can:
- View all available endpoints
- Read detailed API descriptions
- Test API endpoints directly from the browser
- View request/response schemas

## Features

- Clean Architecture implementation
- Dependency Injection using Uber FX
- Structured logging with Zerolog
- Configuration management with Viper
- CORS support
- Swagger API documentation
- Docker support
- Health check endpoint
- MySQL database integration
- GORM ORM for database operations 
# Trip Planner

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
│   ├── dto              # Data Transfer Objects
│   ├── logger           # Logging configuration
│   ├── model            # Data models
│   ├── repository       # Database operations
│   ├── service          # Business logic
│   └── util             # Utility functions
├── docs                 # Swagger documentation
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

<!-- ### Running with Docker

1. Clone the repository:
```bash
git clone https://github.com/ltdoanh2004/Grab-project.git
cd Grab-project/backend
```

2. Start the application using Docker Compose:
```bash
docker-compose up -d
```

The application will be available at `http://localhost:8080` -->

### Running Locally

1. Clone the repository
```bash
git clone https://github.com/ltdoanh2004/Grab-project.git
cd Grab-project/backend
```
2. Create a `.env` file
3. Run Docker MySQL database
```bash
make mysql
```
4. Run the application:
```bash
make server
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
make swag
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
### User Experience
- **Personalized Trip Planning**: Create customized travel itineraries based on preferences
- **AI-Powered Recommendations**: Get intelligent suggestions for destinations, activities, and restaurants
- **Interactive Itinerary Builder**: Drag and drop interface for organizing daily activities
- **Expense Tracking**: Track and split expenses among travel companions
- **Plan Sharing**: Share travel plans with friends and family
- **Export Options**: Export plans to spreadsheets or take screenshots

### Travel Planning Flow
- **Destination Selection**: Choose from popular destinations or discover new places
- **Budget Management**: Set and track travel budget constraints
- **Date Selection**: Flexible date picking with duration optimization
- **Preference Configuration**: Specify travel style, interests, and special requirements
- **AI Plan Generation**: Receive AI-generated itineraries based on your inputs
- **Plan Customization**: Modify suggested plans to perfectly match your preferences

### AI Capabilities
- **Smart Recommendations**: Context-aware suggestions based on user preferences
- **Multi-Source Data**: Recommendations drawn from extensive travel databases
- **Natural Language Processing**: Understand and respond to user requests in natural language
- **Optimization Algorithms**: Create efficient itineraries considering distances, opening hours, and more
- **Personalization**: Learn from user feedback to improve future recommendations
- **Real-time Updates**: Adjust plans based on weather, events, or other changing factors

### Technical Features
- **Responsive Design**: Works seamlessly across desktop, tablet, and mobile devices
- **Secure Authentication**: JWT-based authentication system
- **API Documentation**: Comprehensive Swagger documentation
- **Scalable Architecture**: Microservices-based design for future expansion
- **Data Visualization**: Interactive maps and charts for better planning

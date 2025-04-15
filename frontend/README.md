# Todo Application

[![TypeScript](https://img.shields.io/badge/TypeScript-4.9.5-blue.svg)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-19-blue.svg)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-4.0-646CFF.svg)](https://vitejs.dev/)
[![Ant Design](https://img.shields.io/badge/Ant%20Design-5.0-0170FE.svg)](https://ant.design/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A modern, responsive Todo application built with React, TypeScript, and Ant Design. This project serves as a showcase of best practices in modern frontend development.

## Features

- **Task Management**
  - Create, read, update, and delete todos
  - Task title and description
  - Task status tracking
  - List and grid view options

- **User Experience**
  - Clean and intuitive interface
  - Status management (Pending, In Progress, Completed)
  - Responsive design for all devices
  - Modern Ant Design components

- **Technical Features**
  - Type-safe development with TypeScript
  - Fast development with Vite
  - Efficient API integration with Axios
  - State management with React hooks

## Tech Stack

- React 19
- TypeScript 4.9
- Vite 4.0
- Ant Design 5.0
- Axios
- ESLint + Prettier

## Getting Started

### Prerequisites

- Node.js (v18 or higher recommended)
- yarn or npm

### Installation

1. Clone the repository:
```bash
git clone https://github.com/tuannguyensn2001/skeleton-bootcamp-frontend
cd skeleton-bootcamp-frontend
```

2. Install dependencies:
```bash
yarn install
```

3. Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

4. Update the `.env` file with your API endpoint if needed:
```
VITE_API_BASE_URL=http://localhost:8080/api/v1
```

### Development

To start the development server:

```bash
yarn dev
```

The application will be available at `http://localhost:5173`

### Building for Production

To create a production build:

```bash
yarn build
```

To preview the production build:

```bash
yarn preview
```

### Linting

To run the linter:

```bash
yarn lint
```

## Project Structure

```
src/
├── components/     # React components
├── constants/      # Constants and enums
├── hooks/          # Custom React hooks
├── services/       # API services
├── types/          # TypeScript types and interfaces
└── App.tsx         # Root component
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| VITE_API_BASE_URL | Backend API URL | http://localhost:8080/api/v1 |

## License

This project is licensed under the MIT License.

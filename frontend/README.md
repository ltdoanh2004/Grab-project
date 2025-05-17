# Travel Planner Application

[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-blue.svg)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-19-blue.svg)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-6.2-646CFF.svg)](https://vitejs.dev/)
[![Ant Design](https://img.shields.io/badge/Ant%20Design-5.24-0170FE.svg)](https://ant.design/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-4.1-38B2AC.svg)](https://tailwindcss.com/)
[![React Router](https://img.shields.io/badge/React%20Router-7.5-CA4245.svg)](https://reactrouter.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A modern, responsive Travel Planner application built with React 19, TypeScript, and Ant Design. This project showcases best practices in modern frontend development with an emphasis on user experience and feature-rich travel planning capabilities.

## Features

- **Comprehensive Travel Planning**
  - Multi-step travel plan creation
  - Destination selection with visual guides
  - Budget and traveler configuration
  - Flexible travel date selection
  - AI-powered itinerary generation
  - Personalized preferences for activities, accommodation, and more

- **Travel Plan Management**
  - View all travel plans with filtering options (Upcoming, Ongoing, Completed, All)
  - Detailed day-by-day itinerary views
  - Drag and drop functionality for reordering activities
  - Expense tracking and bill splitting features
  - Export plans to spreadsheets for offline use

- **Authentication System**
  - Secure sign-in and sign-up functionality
  - Token-based authentication
  - Personalized user profiles

- **User Experience**
  - Clean, intuitive interface with modern design patterns
  - Responsive layout for all devices
  - Day and night mode support
  - Offline capability for viewing saved travel plans

## Tech Stack

- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite 6.2
- **UI Library**: Ant Design 5.24
- **Routing**: React Router v7
- **Styling**: TailwindCSS v4
- **API Integration**: Axios
- **State Management**: React Query (TanStack Query)
- **Drag and Drop**: React DnD
- **Other Libraries**: 
  - html2canvas (for itinerary screenshots)
  - xlsx (for spreadsheet exports)

## Getting Started

### Prerequisites

- Node.js (v18 or higher recommended)
- yarn or npm

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/travel-planner
cd travel-planner
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
├── components/        # React components
│   ├── authScreen/    # Authentication components
│   ├── newplan/       # Trip planning components
│   └── planlist/      # Trip management components
├── constants/         # Constants and enums
├── hooks/             # Custom React hooks
├── services/          # API services
├── types/             # TypeScript types and interfaces
├── utils/             # Utility functions
└── App.tsx            # Root component
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| VITE_API_BASE_URL | Backend API URL | http://localhost:8081/api/v1 |

## License

This project is licensed under the MIT License.

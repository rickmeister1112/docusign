# Feedback System with Upvote Functionality

A full-stack web application for managing feedback submissions with upvote capabilities. Built with React + TypeScript + Vite for the frontend and FastAPI + SQLite for the backend.

## 📚 Documentation

- **[Code Review & Issues](CODE_REVIEW.md)** - Comprehensive analysis of code issues and improvements needed
- **[Technical Documentation](TECHNICAL_DOCUMENTATION.md)** - Complete implementation guide with code examples
- **[Improvements Roadmap](IMPROVEMENTS_ROADMAP.md)** - Phased plan for implementing improvements
- **[Setup Guide](SETUP.md)** - Quick setup and troubleshooting
- **[Authentication Summary](AUTHENTICATION_SUMMARY.md)** - Authentication system documentation

## Features

- **Create Feedback**: Submit new feedback entries with text content
- **View Feedback**: Display all feedback entries in a clean, organized layout
- **Upvote Feedback**: Vote for feedback entries you find helpful or agree with
- **Delete Feedback**: Remove feedback entries (with confirmation)
- **Real-time Updates**: See upvote counts update immediately
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Sorting**: Feedback is automatically sorted by upvotes (descending) then by creation date

## Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **CSS3** with modern styling and responsive design
- **Axios** for HTTP requests

### Backend
- **FastAPI** for high-performance API
- **SQLAlchemy** for database ORM
- **SQLite** for data persistence
- **Pydantic** for data validation

## Getting Started

### Prerequisites
- Node.js (v16 or higher)
- Python (v3.8 or higher)
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd interview
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

#### Option 1: Using Startup Scripts (Recommended)

1. **Start the Backend Server**
   ```bash
   ./start-backend.sh
   ```
   The API will be available at `http://localhost:8000`

2. **Start the Frontend Development Server**
   ```bash
   ./start-frontend.sh
   ```
   The application will be available at `http://localhost:5173`

#### Option 2: Manual Commands

1. **Start the Backend Server**
   ```bash
   cd backend
   source .venv/bin/activate  # On Windows: venv\Scripts\activate
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   The API will be available at `http://localhost:8000`

2. **Start the Frontend Development Server**
   ```bash
   cd frontend
   npm run dev
   ```
   The application will be available at `http://localhost:5173`

#### Backend Troubleshooting

If you encounter the error `ERROR: Error loading ASGI app. Could not import module "app.main"`:

- **Make sure you're in the correct directory**: Run the command from the `backend` directory, not the project root
- **Check virtual environment**: Ensure the virtual environment is activated with `source .venv/bin/activate`
- **Verify dependencies**: Make sure all requirements are installed with `pip install -r requirements.txt`

#### API Documentation

Once the backend is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc
- **OpenAPI schema**: http://localhost:8000/openapi.json

## API Endpoints

### Feedback Management
- `GET /feedback/` - Get all feedback entries (ordered by upvotes, then creation date)
- `POST /feedback/` - Create a new feedback entry
- `GET /feedback/{id}` - Get a specific feedback entry
- `PUT /feedback/{id}` - Update a feedback entry
- `DELETE /feedback/{id}` - Delete a feedback entry

### Upvote Functionality
- `POST /feedback/{id}/upvote` - Upvote a feedback entry

## Database Schema

### Feedback Table
- `id` (INTEGER, PRIMARY KEY) - Unique identifier
- `text` (TEXT, NOT NULL) - Feedback content
- `upvotes` (INTEGER, DEFAULT 0, NOT NULL) - Number of upvotes
- `created_at` (DATETIME) - Creation timestamp
- `updated_at` (DATETIME) - Last update timestamp

## Features in Detail

### Upvote System
- Each feedback entry can be upvoted by clicking the 👍 button
- Upvote counts are displayed next to the button
- Feedback is automatically sorted by upvote count (highest first)
- Upvotes are persisted in the database
- Real-time UI updates when upvoting

### User Interface
- Clean, modern design with intuitive navigation
- Responsive layout that works on all device sizes
- Loading states and error handling
- Confirmation dialogs for destructive actions
- Visual feedback for user interactions

### Data Management
- Automatic sorting by popularity (upvotes) and recency
- Pagination support for large datasets
- Optimistic UI updates for better user experience
- Comprehensive error handling and validation

## Development

### Project Structure
```
interview/
├── backend/
│   ├── app/
│   │   ├── __init__.py      # Python package marker
│   │   ├── main.py          # FastAPI application
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── crud.py          # Database operations
│   │   ├── database.py      # Database configuration
│   │   └── auth.py          # Authentication utilities
│   ├── venv/                # Python virtual environment
│   ├── requirements.txt     # Python dependencies
│   └── feedback.db          # SQLite database
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   ├── types/           # TypeScript types
│   │   └── App.tsx          # Main application
│   ├── package.json         # Node.js dependencies
│   └── vite.config.ts       # Vite configuration
└── README.md
```

### Adding New Features
1. Update the database model in `backend/app/models.py`
2. Add corresponding Pydantic schemas in `backend/app/schemas.py`
3. Implement CRUD operations in `backend/app/crud.py`
4. Add API endpoints in `backend/app/main.py`
5. Update TypeScript types in `frontend/src/types/`
6. Add API service methods in `frontend/src/services/api.ts`
7. Update React components in `frontend/src/components/`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 
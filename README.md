# DocNearby

DocNearby is a full-stack web application that helps users find nearby doctors, book appointments, and manage health insights. The project consists of a Django REST API backend and a React frontend.

## Project Structure

- `docnearby_project/` - Django backend (API, authentication, appointments, feedback, symptoms, users, doctors)
- `docnearby-frontend/` - React frontend (user interface)

## Features
- Doctor search and filtering
- Appointment booking and management
- Patient and doctor dashboards
- Symptom analysis and health insights
- Feedback system

## Getting Started

### Backend (Django)
1. Navigate to the backend directory:
   ```bash
   cd docnearby_project
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```
4. Run migrations and start the server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

### Frontend (React)
1. Navigate to the frontend directory:
   ```bash
   cd docnearby-frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm start
   ```

## License
See [LICENSE](LICENSE) for details. 
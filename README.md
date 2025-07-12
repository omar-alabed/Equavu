# Equavo HR System

A minimal HR system allowing job applicants to register as candidates and upload their resumes, while HR managers can log in, view the list of candidates, and download their resumes.

## Features

### Candidate Functionality
- Registration with personal details and resume upload
- Application status tracking
- Resume validation and storage
- Email notifications on status changes and registration confirmation
- Conditional Resume Storage: Resumes are stored locally or uploaded to Amazon S3, depending on configuration.
If S3 is enabled in settings, resumes are uploaded securely to your S3 bucket;
otherwise, they are saved in the local media/resumes directory.

### Admin Functionality
- List candidates with filtering and pagination
- Update application status with feedback
- Download candidate resumes
- Track status change history

### Other Features
- **React Frontend**: User-friendly interface for candidates and admins
- **Swagger Documentation**: Interactive API documentation
- **Comprehensive Tests**: Unit and integration tests
- **Docker Support**: Easy deployment with Docker Compose

## Technology Stack

- **Backend**: Python 3 + Django + Django REST Framework
- **Frontend**: React with Bootstrap
- **Database**: MySQL
- **API Documentation**: Swagger/OpenAPI (drf-spectacular)
- **File Storage**: Local storage with abstraction layer for future cloud migration
- **Authentication**: Simple header-based admin authentication
- **Testing**: pytest and pytest-django
- **Deployment**: Docker and Docker Compose

## Setup Instructions

There are two ways to set up the application: using Docker (recommended) or traditional setup.

### Option 1: Docker Setup (Recommended)

#### Prerequisites

- Docker
- Docker Compose

#### Installation

1. Clone the repository:
   ```
   git clone https://github.com/omar-alabed/Equavu.git
   cd equavo
   ```

2. Start the application using Docker Compose:
   ```
   docker-compose up -d
   ```

3. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost/api/
   - Swagger Documentation: http://localhost/api/docs/swagger/
   - Redoc Documentation: http://localhost/api/docs/redoc/

4. To stop the application:
   ```
   docker-compose down
   ```

### Option 2: Traditional Setup

#### Prerequisites

- Python 3.8+
- MySQL
- Node.js and npm
- pip

#### Backend Installation

1. Clone the repository:
   ```
   git clone https://github.com/omar-alabed/Equavu.git
   cd equavo
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables (optional):
   ```
   export DB_NAME=equavu_hr
   export DB_USER=root
   export DB_PASSWORD=root
   export DB_HOST=localhost
   export DB_PORT=3306
   ```

5. Create necessary directories:
   ```
   mkdir -p media/resumes
   mkdir -p logs
   mkdir -p staticfiles
   ```

6. Run database migrations:
   ```
   python manage.py migrate
   ```

7. Collect static files:
   ```
   python manage.py collectstatic --noinput
   ```

8. Start the development server:
   ```
   python manage.py runserver
   ```

#### Frontend Installation

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

4. Access the frontend at http://localhost:3000

### Running Tests

To run the tests:

```
pytest
```

For more detailed test output:

```
pytest -v
```

To run specific test files:

```
pytest equavu_hr_app/tests/test_models.py
pytest equavu_hr_app/tests/test_serializers.py
pytest equavu_hr_app/tests/test_views.py
```

## API Documentation

The API is documented using Swagger/OpenAPI. When the application is running, you can access the interactive documentation at:

- Swagger UI: http://localhost/api/docs/swagger/
- ReDoc: http://localhost/api/docs/redoc/

### Authentication

Admin endpoints require the `X-ADMIN` header:
```
X-ADMIN: 1
```

### Endpoints

#### Candidate Endpoints

1. **Register Candidate**
   - URL: `POST /api/candidates/register/`
   - Description: Register a new candidate with personal details and resume
   - Request Body:
     ```json
     {
       "full_name": "Omar Alabed",
       "email": "o.alabed94@gmail.com",
       "date_of_birth": "1994-07-26",
       "years_of_experience": 6,
       "department": "IT",
       "resume": [file upload]
     }
     ```
   - Response: 201 Created

2. **Check Application Status**
   - URL: `GET /api/candidates/{candidate_id}/status/`
   - Description: Check the status of a candidate's application
   - Response:
     ```json
     {
       "id": "uuid",
       "full_name": "Omar Alabed",
       "email": "o.alabed94@gmail.com",
       "date_of_birth": "1994-07-26",
       "years_of_experience": 6,
       "department": "IT",
       "department_display": "IT",
       "current_status": "SUBMITTED",
       "current_status_display": "Submitted",
       "created_at": "2025-07-12T12:00:00Z",
       "updated_at": "2025-07-12T12:00:00Z",
       "status_changes": [
         {
           "id": "uuid",
           "previous_status": null,
           "new_status": "SUBMITTED",
           "feedback": "Application submitted successfully.",
           "admin_user": "",
           "created_at": "2025-07-12T12:00:00Z"
         }
       ]
     }
     ```

#### Admin Endpoints

1. **List Candidates**
   - URL: `GET /api/admin/candidates/`
   - Description: List all candidates with pagination
   - Headers: `X-ADMIN: 1`
   - Query Parameters:
     - `department`: Filter by department (IT, HR, FINANCE)
     - `page`: Page number for pagination
   - Response:
     ```json
     {
       "count": 10,
       "next": "http://localhost/api/admin/candidates/?page=2",
       "previous": null,
       "results": [
         {
           "id": "uuid",
           "full_name": "Omar Alabed",
           "date_of_birth": "1994-07-26",
           "years_of_experience": 6,
           "department": "IT",
           "department_display": "IT",
           "current_status": "SUBMITTED",
           "current_status_display": "Submitted",
           "created_at": "2025-07-12T12:00:00Z"
         }
       ]
     }
     ```

2. **View Candidate Details**
   - URL: `GET /api/admin/candidates/{candidate_id}/`
   - Description: View detailed information about a candidate
   - Headers: `X-ADMIN: 1`
   - Response: Same as Check Application Status endpoint

3. **Update Application Status**
   - URL: `PUT /api/admin/candidates/{candidate_id}/status/`
   - Description: Update a candidate's application status
   - Headers: 
     - `X-ADMIN: 1`
     - `X-ADMIN-USER: Admin Name` (optional)
   - Request Body:
     ```json
     {
       "status": "UNDER_REVIEW",
       "feedback": "Your application is being reviewed by our team."
     }
     ```
   - Response:
     ```json
     {
       "message": "Status updated successfully",
       "candidate": {
         // Candidate details
       }
     }
     ```

4. **Download Resume**
   - URL: `GET /api/admin/candidates/{candidate_id}/resume/`
   - Description: Download a candidate's resume
   - Headers: `X-ADMIN: 1`
   - Response: File download

## File Storage

The system uses a storage abstraction layer that allows for easy switching between local and cloud storage solutions. Currently, files are stored locally in the `media/resumes` directory, but the system is designed to allow future migration to cloud storage (S3, Azure, etc.).

## Frontend Application

The system includes a React frontend application that provides a user-friendly interface for:

1. **Candidate Features**
   - Registration form with resume upload
   - Application status checking

2. **Admin Features**
   - Candidate listing with filtering and pagination
   - Detailed candidate view
   - Status update functionality
   - Resume download

The frontend is built with React and uses Bootstrap for styling. It communicates with the backend API using Axios.

## Database Schema

The system uses MySQL as the database and has two main models:

1. **Candidate**
   - UUID primary key
   - Personal details (full name, email, date of birth, years of experience)
   - Department (IT, HR, Finance)
   - Resume file
   - Current application status
   - Created/updated timestamps

2. **StatusChange**
   - UUID primary key
   - Reference to Candidate
   - Previous and new status
   - Feedback
   - Admin user information
   - Created timestamp

## Performance Considerations

- Database indexes are used for frequently queried fields
- Pagination is implemented for listing candidates
- File size validation ensures uploads don't exceed 5MB
- The system is designed to handle at least 100,000 candidate records efficiently

## Security Considerations

- Input validation for all fields
- File type validation for resume uploads
- Error handling for file operations
- Logging for key events

 ## FitTrack API ##
A secure, scalable FastAPI application for fitness tracking — aligned with SDG 3: Good
Health and Well-Being
 Project Overview

## FitTrack is a RESTful API built with FastAPI that helps users in Sierra Leone track their
fitness journey — including workouts, nutrition, body measurements, and personal goals. It
addresses SDG 3 (Good Health and Well-Being) by democratising access to health tracking
tools.
Course: PROG315 — Object-Oriented Programming 2
Institution: Limkokwing University of Creative Technology, Sierra Leone
Semester: 4 (March 2026 – July 2026)
 
 ## Core Requirements Coverage
Requirement Implementation
Framework FastAPI
CRUD Operations All resources: workouts, nutrition, progress, goals
Database Integration PostgreSQL + SQLAlchemy ORM
Dependency Injection Depends(get_db) on every route
Authentication OAuth2 + JWT (python-jose + bcrypt)
REST Standards RESTful endpoints, proper HTTP methods & status codes
Auto Documentation Swagger UI (/docs) + ReDoc (/redoc)
Async Programming async def routes + async calorie estimation
Type Annotations Pydantic schemas + Python type hints throughout

## SDG Alignment ##
Open-Source License
SDG 3 — Good Health and Well-Being
MIT License
 
 ## Project Structure
fitness_tracker/
├── main.py             # App entry point, router registration
├── database.py         # SQLAlchemy engine, session, get_db dependency
├── models.py           # SQLAlchemy ORM models
├── schemas.py          # Pydantic request/response schemas
├── auth.py             # JWT creation, password hashing, user dependencies
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── routers/
├── auth_router.py  # /auth — register, login, profile
├── workouts.py     # /workouts — CRUD + exercises
├── nutrition.py    # /nutrition — meal logging + daily summary
├── progress.py     # /progress — body measurements
├── goals.py        # /goals — fitness goals
└── admin.py        # /admin — admin-only user management
 
 ## Getting Started
1. Clone the Repository
git clone https://github.com/YOUR_USERNAME/fittrack-api.git
cd fittrack-api
2. Create Virtual Environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
3. Install Dependencies
pip install -r requirements.txt
4. Configure Environment Variables
cp .env.example .env
Edit .env with your PostgreSQL credentials and a strong SECRET_KEY
5. Create the PostgreSQL Database
CREATE DATABASE fitness_tracker;
6. Run the Application
uvicorn main:app --reload
7. Access the API Docs
Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc
 
 ## API Endpoints
Authentication ( /auth )
Method
Endpoint
Description
POST
/auth/register
Register a new user
POST
/auth/token
Login — receive JWT token
GET
/auth/me
Get current user profile
PUT
/auth/me
Update current user profile
Workouts ( /workouts )
Method
Endpoint
Description
POST
/workouts/
Log a new workout
GET /workouts/ List all workouts
GET /workouts/{id} Get workout by ID
PUT /workouts/{id} Update a workout
DELETE /workouts/{id} Delete a workout
POST /workouts/{id}/exercises Add exercise to workout
DELETE /workouts/{id}/exercises/{ex_id} Remove exercise
Nutrition (/nutrition)
Method Endpoint Description
POST /nutrition/ Log a meal
GET /nutrition/ List all meal logs
GET /nutrition/summary Daily macro summary
GET /nutrition/{id} Get meal log by ID
PUT /nutrition/{id} Update meal log
DELETE /nutrition/{id} Delete meal log
Progress (/progress)
Method Endpoint Description
POST /progress/ Record body measurements
GET /progress/ List all progress entries
GET /progress/latest Get most recent entry
GET /progress/{id} Get entry by ID
DELETE /progress/{id} Delete entry
Goals (/goals)
Method Endpoint Description
POST /goals/ Create a fitness goal
GET /goals/ List all goals
GET /goals/{id} Get goal by ID
PUT /goals/{id} Update / mark achieved
DELETE /goals/{id} Delete goal
Admin (/admin)
Method Endpoint Description
GET /admin/users List all users (admin only)
DELETE /admin/users/{id} Delete user (admin only)
PATCH /admin/users/{id}/deactivate Deactivate user (admin only)
 ## Authentication Flow ##
1. Register via POST /auth/register
2. Login via POST /auth/token — receive access_token
3. Include in all protected requests: Authorization: Bearer <token>
 SDG Alignment
SDG 3 — Good Health and Well-Being
FitTrack addresses the lack of accessible health and fitness tools in Sierra Leone. By
providing a free, open-source API, it enables developers to build mobile or web applications
that promote physical activity, balanced nutrition, and healthy lifestyle habits — contributing
directly to SDG 3 targets.
 License
This project is licensed under the MIT License — see 
LICENSE for details.
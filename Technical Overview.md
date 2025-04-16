🚀 Frameworks & Tools
FastAPI
Purpose: Main web framework for building APIs.

Key Features Used:

Dependency injection

Pydantic for data validation

Built-in exception handling

Asynchronous support

Pydantic
Purpose: Data modeling and validation for request and response schemas.

Usage: Defined BaseModel classes like StudentCreate, StudentUpdate, etc.

Uvicorn (assumed)
Purpose: ASGI server used to run FastAPI apps.

Benefit: High performance for async I/O.

SQLAlchemy (assumed via crud usage)
Purpose: ORM (Object Relational Mapper) for interacting with the database.

Usage: CRUD operations in src/data/database/crud.py.

CORS Middleware
Purpose: Allowing frontend clients to interact with the API.

Config:

allow_origins=["http://0.0.0.0:5500", "http://localhost:5500"]

allow_methods=["*"], allow_headers=["*"]

FastAPI StaticFiles
Purpose: Serves frontend files (HTML, CSS, JS).

Directory: src/web is mounted at /static.

📁 API Design & Endpoints
Students API
Create, read (by ID and name), update, delete

Data: name, traits, strengths, weaknesses, motivations, fears, communication style

Scenarios API
Manage classroom situations or case studies

Dialogues API
Represents conversations between a student and teacher in a scenario

File Management API
Uploading and toggling files between active/inactive

Handles markdown file ingestion for educational content

Health Check Endpoint
/database-health: Verifies database connectivity

Chat Endpoint
/chat: Placeholder for future AI chatbot integration

📦 Models & Serialization
Each main entity (Student, Scenario, Dialogue, File) has:

BaseModel for shared fields

Create, Update, Response models for different use cases

All response models use orm_mode = True for SQLAlchemy compatibility.

💬 Planned AI Integration
Chat Endpoint (placeholder)
Route: /chat

Planned Use: Integrate with an LLM (e.g., OpenAI GPT, LLaMA, or custom model) for interactive teacher training

⚙️ Assumed Additions (Behind the Scenes)
Database: Likely SQLite or PostgreSQL

File Storage: Handled in-memory or stored via BLOBs in the DB

Environment: Localhost testing on port 5500 with HTML front-end

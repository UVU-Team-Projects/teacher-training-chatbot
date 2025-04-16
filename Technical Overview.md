# Technical Overview

## ✨ Frameworks & Tools

### FastAPI
- **Purpose**: Main web framework for building APIs.
- **Highlights**:
  - Asynchronous route support
  - Pydantic for data validation
  - Auto-generated OpenAPI docs

### Pydantic
- **Purpose**: Data modeling and validation for request and response schemas.
- **Usage**: Used for request validation (`StudentCreate`, `ScenarioUpdate`, etc.)

### SQLAlchemy *(Assumed)*
- **Purpose**: ORM for database access.
- **Used in**: `src/data/database/crud.py` for all database operations.

### CORS Middleware
- **Purpose**: Enables front-end communication with the API.
- **Allowed Origins**: `http://0.0.0.0:5500`, `http://localhost:5500`

### StaticFiles
- **Purpose**: Serves HTML, JS, and CSS assets from the `src/web` directory.

---

## 📄 API Overview

### Students API
- Endpoints:
  - `GET /students`
  - `POST /students`
  - `PUT /students/{id}`
  - `DELETE /students/{id}`
- Features: Stores name, traits, motivations, communication styles, etc.

### Scenarios API
- Manages classroom scenarios for teacher training.
- Endpoints:
  - `GET /scenarios`
  - `POST /scenarios`
  - `PUT /scenarios/{id}`

### Dialogues API
- Represents conversations tied to students and scenarios.
- Endpoints:
  - `GET /dialogues/by-scenario/{id}`
  - `POST /dialogues`

### File Management API
- Manages educational files (e.g., markdown lesson content).
- Key Features:
  - Upload files
  - Move between active/inactive states
  - Query by name or ID

### Health Check
- Endpoint: `GET /database-health`
- Confirms database connectivity.

---

## 🔎 Planned: AI Chatbot Integration
- Route: `POST /chat`
- Current: Returns default static response
- Future: Will connect to an LLM for real-time classroom simulation dialogue

---

## 🔢 Models & Serialization
- All main entities (Students, Scenarios, Dialogues, Files) use:
  - `BaseModel` + `Create`, `Update`, and `Response` classes
  - Pydantic with `orm_mode = True` for ORM compatibility



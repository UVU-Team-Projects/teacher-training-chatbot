from fastapi import FastAPI, HTTPException, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
from src.data.database import crud
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime

app = FastAPI()

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://0.0.0.0:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static files directory
app.mount("/static", StaticFiles(directory="src/web"), name="static")

# ---------------------------------------------
# Models for Students
# ---------------------------------------------
class StudentBase(BaseModel):
    name: str
    traits: List[str]
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    motivations: Optional[List[str]] = None
    fears: Optional[List[str]] = None
    communication_style: Optional[str] = None

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    traits: Optional[List[str]] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    motivations: Optional[List[str]] = None
    fears: Optional[List[str]] = None
    communication_style: Optional[str] = None

class StudentResponse(StudentBase):
    id: int

    class Config:
        orm_mode = True

# ---------------------------------------------
# Endpoints for Student CRUD
# ---------------------------------------------
@app.get("/students", response_model=List[StudentResponse])
def get_all_students():
    return crud.get_all_students()

@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int):
    student = crud.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.get("/students/by-name/{student_name}", response_model=StudentResponse)
def get_student_by_name(student_name: str):
    student = crud.get_student_by_name(student_name)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.post("/students", response_model=StudentResponse)
def create_student(student: StudentCreate):
    new_student = crud.create_student(
        name=student.name,
        traits=student.traits,
        strengths=student.strengths,
        weaknesses=student.weaknesses,
        motivations=student.motivations,
        fears=student.fears,
        communication_style=student.communication_style
    )
    if not new_student:
        raise HTTPException(
            status_code=400,
            detail="Student creation failed (possibly duplicate or invalid data)"
        )
    return new_student

@app.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student_update: StudentUpdate):
    update_data = student_update.dict(exclude_unset=True)
    updated_student = crud.update_student(student_id, **update_data)
    if not updated_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return updated_student

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    if not crud.delete_student(student_id):
        raise HTTPException(status_code=404, detail="Student not found")
    return {"detail": "Student deleted successfully"}

# ---------------------------------------------
# Models for Scenarios
# ---------------------------------------------
class ScenarioBase(BaseModel):
    title: str
    description: str

class ScenarioCreate(ScenarioBase):
    pass

class ScenarioUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class ScenarioResponse(ScenarioBase):
    id: int

    class Config:
        orm_mode = True

# ---------------------------------------------
# Endpoints for Scenario CRUD
# ---------------------------------------------
@app.get("/scenarios", response_model=List[ScenarioResponse])
def get_all_scenarios():
    return crud.get_all_scenarios()

@app.get("/scenarios/by-title/{title}", response_model=ScenarioResponse)
def get_scenario_by_title(title: str):
    scenario = crud.get_scenario_by_title(title)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario

@app.post("/scenarios", response_model=ScenarioResponse)
def create_scenario(scenario: ScenarioCreate):
    new_scenario = crud.create_scenario(scenario.title, scenario.description)
    if not new_scenario:
        raise HTTPException(status_code=400, detail="Scenario creation failed")
    return new_scenario

@app.put("/scenarios/{scenario_id}", response_model=ScenarioResponse)
def update_scenario(scenario_id: int, scenario_update: ScenarioUpdate):
    update_data = scenario_update.dict(exclude_unset=True)
    updated_scenario = crud.update_scenario(scenario_id, **update_data)
    if not updated_scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return updated_scenario

@app.delete("/scenarios/{scenario_id}")
def delete_scenario(scenario_id: int):
    if not crud.delete_scenario(scenario_id):
        raise HTTPException(status_code=404, detail="Scenario deletion failed or not found")
    return {"detail": "Scenario deleted successfully"}

# ---------------------------------------------
# Models for Dialogues
# ---------------------------------------------
class DialogueBase(BaseModel):
    scenario_id: int
    student_name: str
    utterance: str

class DialogueCreate(DialogueBase):
    pass

class DialogueUpdate(BaseModel):
    student_name: Optional[str] = None
    utterance: Optional[str] = None

class DialogueResponse(DialogueBase):
    id: int

    class Config:
        orm_mode = True

# ---------------------------------------------
# Endpoints for Dialogue CRUD
# ---------------------------------------------
@app.get("/dialogues/{dialogue_id}", response_model=DialogueResponse)
def get_dialogue(dialogue_id: int):
    dialogue = crud.get_dialogue_by_id(dialogue_id)
    if not dialogue:
        raise HTTPException(status_code=404, detail="Dialogue not found")
    return dialogue

@app.get("/dialogues/by-scenario/{scenario_id}", response_model=List[DialogueResponse])
def get_dialogues_by_scenario(scenario_id: int):
    return crud.get_dialogues_by_scenario(scenario_id)

@app.get("/dialogues/by-student-and-scenario", response_model=List[DialogueResponse])
def get_dialogues_by_student_and_scenario(student_name: str, scenario_title: str):
    return crud.get_dialogues_by_student_and_scenario(student_name, scenario_title)

@app.post("/dialogues", response_model=DialogueResponse)
def create_dialogue(dialogue: DialogueCreate):
    new_dialogue = crud.create_dialogue(dialogue.scenario_id, dialogue.student_name, dialogue.utterance)
    if not new_dialogue:
        raise HTTPException(status_code=400, detail="Dialogue creation failed")
    return new_dialogue

@app.put("/dialogues/{dialogue_id}", response_model=DialogueResponse)
def update_dialogue(dialogue_id: int, dialogue_update: DialogueUpdate):
    update_data = dialogue_update.dict(exclude_unset=True)
    updated_dialogue = crud.update_dialogue(dialogue_id, **update_data)
    if not updated_dialogue:
        raise HTTPException(status_code=404, detail="Dialogue not found")
    return updated_dialogue

@app.delete("/dialogues/{dialogue_id}")
def delete_dialogue(dialogue_id: int):
    if not crud.delete_dialogue(dialogue_id):
        raise HTTPException(status_code=404, detail="Dialogue deletion failed or not found")
    return {"detail": "Dialogue deleted successfully"}

# ---------------------------------------------
# Models and Endpoints for File Operations
# ---------------------------------------------
class FileResponseModel(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

@app.get("/files/active/{file_id}", response_model=FileResponseModel)
def get_active_file(file_id: int):
    file = crud.get_active_file_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="Active file not found")
    return file

@app.get("/files/active/by-name/{name}", response_model=FileResponseModel)
def get_active_file_by_name(name: str):
    file = crud.get_active_file_by_name(name)
    if not file:
        raise HTTPException(status_code=404, detail="Active file not found")
    return file

@app.get("/files/inactive/{file_id}", response_model=FileResponseModel)
def get_inactive_file(file_id: int):
    file = crud.get_inactive_file_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="Inactive file not found")
    return file

@app.get("/files/inactive/by-name/{name}", response_model=FileResponseModel)
def get_inactive_file_by_name(name: str):
    file = crud.get_inactive_file_by_name(name)
    if not file:
        raise HTTPException(status_code=404, detail="Inactive file not found")
    return file

@app.post("/files/active", response_model=FileResponseModel)
async def upload_active_file(file: UploadFile = File(...)):
    file_content = await file.read()
    active_file = crud.create_active_file(file.filename, file_content)
    if not active_file:
        raise HTTPException(status_code=400, detail="File upload failed")
    return active_file

@app.put("/files/move-to-inactive/{file_id}")
def move_file_to_inactive(file_id: int):
    if not crud.move_file_to_inactive_by_id(file_id):
        raise HTTPException(status_code=404, detail="Active file not found or move failed")
    return {"detail": "File moved to inactive successfully"}

@app.put("/files/move-to-active/{file_id}")
def move_file_to_active(file_id: int):
    if not crud.move_file_to_active_by_id(file_id):
        raise HTTPException(status_code=404, detail="Inactive file not found or move failed")
    return {"detail": "File moved to active successfully"}

@app.put("/files/move-to-inactive/by-name/{name}")
def move_file_to_inactive_by_name(name: str):
    if not crud.move_file_to_inactive_by_name(name):
        raise HTTPException(status_code=404, detail="Active file with given name not found or move failed")
    return {"detail": "File moved to inactive successfully"}

@app.put("/files/move-to-active/by-name/{name}")
def move_file_to_active_by_name(name: str):
    if not crud.move_file_to_active_by_name(name):
        raise HTTPException(status_code=404, detail="Inactive file with given name not found or move failed")
    return {"detail": "File moved to active successfully"}

@app.post("/files/markdown")
def add_markdown_files():
    crud.add_markdown_files()
    return {"detail": "Markdown files added to active files"}

@app.get("/files/active")
def get_active_files():
    try:
        return crud.get_all_active_files()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/inactive")
def get_inactive_files():
    try:
        return crud.get_all_inactive_files()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/database-health")
def database_health():
    try:
        # Try to access the database through crud
        crud.get_all_students()
        return {"status": "healthy", "message": "Database connection successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint to send a message to the AI chatbot and get a response.
    Currently returns a default message for testing purposes.
    """
    try:
        # Return a default response for now
        default_response = "This is a default response. AI integration coming soon!"
        return ChatResponse(response=default_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")
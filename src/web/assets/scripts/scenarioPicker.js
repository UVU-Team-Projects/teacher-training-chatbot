import { apiEndpoints, fetchFromAPI } from './apiUtils.js';

let selectedStudent = null;
let selectedScenario = null;

document.addEventListener("DOMContentLoaded", () => {
    setupEventListeners();
    loadStudentsFromAPI();
});

function setupEventListeners() {
    document.getElementById("backToStudents").addEventListener("click", showStudentSection);
}

async function loadStudentsFromAPI() {
    try {
        const students = await fetchFromAPI(apiEndpoints.students);
        const grid = document.getElementById("studentGrid");
        grid.innerHTML = "";
        
        // First card: Create New Student
        grid.appendChild(createNewItemCard("student"));
        
        // Add existing student cards
        students.forEach(student => {
            grid.appendChild(createStudentCard(student));
        });
    } catch (error) {
        console.error("Error loading students:", error);
        alert("Failed to load students from database");
    }
}

async function loadScenariosFromAPI() {
    try {
        const scenarios = await fetchFromAPI(apiEndpoints.scenarios);
        const grid = document.getElementById("scenarioGrid");
        grid.innerHTML = "";
        
        // First card: Create New Scenario
        grid.appendChild(createNewItemCard("scenario"));
        
        // Add existing scenario cards
        scenarios.forEach(scenario => {
            grid.appendChild(createScenarioCard(scenario));
        });
    } catch (error) {
        console.error("Error loading scenarios:", error);
        alert("Failed to load scenarios from database");
    }
}

function createNewItemCard(type) {
    const card = document.createElement("div");
    card.classList.add("card", "new-item-card");
    
    const header = document.createElement("div");
    header.classList.add("card-header");
    header.textContent = "Create New " + capitalize(type);
    
    const body = document.createElement("div");
    body.classList.add("card-body");
    body.textContent = "Click here to create a new " + type;
    
    card.appendChild(header);
    card.appendChild(body);
    
    card.addEventListener("click", () => {
        type === "student" ? addNewStudent() : addNewScenario();
    });
    
    return card;
}

function createStudentCard(student) {
    const card = document.createElement("div");
    card.classList.add("card");
    
    const header = document.createElement("div");
    header.classList.add("card-header");
    header.textContent = student.name;
    
    const body = document.createElement("div");
    body.classList.add("card-body");
    // If traits exist, join them with a comma; otherwise use an empty string.
    body.textContent = student.traits ? student.traits.join(", ") : "";
    
    card.appendChild(header);
    card.appendChild(body);
    
    card.addEventListener("click", () => {
        selectedStudent = student;
        showScenarioSection();
    });
    
    return card;
}

function createScenarioCard(scenario) {
    const card = document.createElement("div");
    card.classList.add("card");
    
    const header = document.createElement("div");
    header.classList.add("card-header");
    header.textContent = scenario.title;
    
    const body = document.createElement("div");
    body.classList.add("card-body");
    body.textContent = scenario.description;
    
    card.appendChild(header);
    card.appendChild(body);
    
    card.addEventListener("click", () => {
        selectedScenario = scenario;
        createChatSession();
    });
    
    return card;
}

function showStudentSection() {
    document.getElementById("scenarioSection").classList.add("hidden");
    document.getElementById("studentSection").classList.remove("hidden");
    selectedScenario = null;
}

function showScenarioSection() {
    document.getElementById("studentSection").classList.add("hidden");
    document.getElementById("scenarioSection").classList.remove("hidden");
    loadScenariosFromAPI();
}

function createChatSession() {
    if (!selectedStudent || !selectedScenario) {
        alert("Please select both a student and a scenario");
        return;
    }
    
    const newSession = {
        id: Date.now().toString(),
        student: selectedStudent.name,
        scenario: selectedScenario.title,
        timestamp: Date.now(),
        chatLog: [{
            sender: "system",
            text: `Starting chat with ${selectedStudent.name} about ${selectedScenario.title}`,
            timestamp: new Date().toISOString()
        }]
    };
    
    const sessions = JSON.parse(localStorage.getItem("chatSessions")) || [];
    sessions.push(newSession);
    localStorage.setItem("chatSessions", JSON.stringify(sessions));
    localStorage.setItem("activeChatSessionId", newSession.id);
    
    // Navigate to the chat page
    window.location.href = "chatPage.html";
}

async function addNewStudent() {
    const name = prompt("Enter the student's name:");
    if (!name) return;
    const traitsInput = prompt("Enter student traits (comma-separated):");
    const traits = traitsInput ? traitsInput.split(",").map(s => s.trim()) : [];
    try {
        await fetchFromAPI(apiEndpoints.students, {
            method: 'POST',
            body: JSON.stringify({
                name,
                traits,
                strengths: [],
                weaknesses: [],
                motivations: [],
                fears: [],
                communication_style: ""
            })
        });
        await loadStudentsFromAPI();
    } catch (error) {
        console.error("Error creating student:", error);
        alert("Failed to create new student");
    }
}

async function addNewScenario() {
    const title = prompt("Enter the scenario title:");
    if (!title) return;
    const description = prompt("Enter the scenario description:");
    if (!description) return;
    try {
        await fetchFromAPI(apiEndpoints.scenarios, {
            method: 'POST',
            body: JSON.stringify({ title, description })
        });
        await loadScenariosFromAPI();
    } catch (error) {
        console.error("Error creating scenario:", error);
        alert("Failed to create new scenario");
    }
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

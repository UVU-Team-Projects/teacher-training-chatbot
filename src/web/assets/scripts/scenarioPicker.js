document.addEventListener("DOMContentLoaded", () => {
    setupSelectionLists();

    document.getElementById("startChatBtn").addEventListener("click", createChatSession);
    document.getElementById("newStudentBtn").addEventListener("click", addNewStudent);
    document.getElementById("newScenarioBtn").addEventListener("click", addNewScenario);
    
    document.getElementById("selectedStudent").addEventListener("click", () => toggleList("studentList"));
    document.getElementById("selectedScenario").addEventListener("click", () => toggleList("scenarioList"));
});

let students = [
    { name: "Alex", personality: "Curious and friendly" },
    { name: "Mia", personality: "Shy but intelligent" },
    { name: "Jake", personality: "Funny but easily distracted" },
    { name: "Sarah", personality: "Serious and competitive" },
    { name: "Chris", personality: "Easygoing and supportive" }
];

let scenarios = [
    { title: "Math Help", description: "You are struggling with fractions in class." },
    { title: "Science Experiment", description: "You have a chemistry project due tomorrow." },
    { title: "History Debate", description: "You are preparing for a history debate on WW2." },
    { title: "English Essay", description: "You need help structuring your essay." },
    { title: "Physics Question", description: "You want to understand Newton's laws." }
];

let selectedStudent = null;
let selectedScenario = null;

function setupSelectionLists() {
    renderSelectionList("studentList", students, selectStudent);
    renderSelectionList("scenarioList", scenarios, selectScenario);
}

function renderSelectionList(containerId, items, onSelect) {
    const container = document.getElementById(containerId);
    container.innerHTML = ""; 

    let scrollableDiv = document.createElement("div");
    scrollableDiv.classList.add("scrollable-list");

    items.forEach((item) => {
        let itemDiv = document.createElement("div");
        itemDiv.classList.add("list-item");
        itemDiv.textContent = item.name ? `${item.name} - ${item.personality}` : `${item.title}`;
        itemDiv.addEventListener("click", () => {
            onSelect(item);
            toggleList(containerId, false); // Close list after selection
        });

        scrollableDiv.appendChild(itemDiv);
    });

    container.appendChild(scrollableDiv);
}

function toggleList(listId, forceOpen = null) {
    const list = document.getElementById(listId);
    
    if (forceOpen !== null) {
        list.classList.toggle("open", forceOpen);
    } else {
        list.classList.toggle("open");
    }
}

function selectStudent(student) {
    selectedStudent = student;
    updateSelectedDisplay("selectedStudent", student.name);
}

function selectScenario(scenario) {
    selectedScenario = scenario;
    updateSelectedDisplay("selectedScenario", scenario.title);
}

function updateSelectedDisplay(elementId, text) {
    const element = document.getElementById(elementId);
    element.textContent = text;
    element.classList.add("selected");
}

function addNewStudent() {
    let name = prompt("Enter the student's name:");
    let personality = prompt("Enter the student's personality:");

    if (name && personality) {
        let newStudent = { name, personality };
        students.push(newStudent);
        setupSelectionLists();
    }
}

function addNewScenario() {
    let title = prompt("Enter the scenario title:");
    let description = prompt("Enter the scenario description:");

    if (title && description) {
        let newScenario = { title, description };
        scenarios.push(newScenario);
        setupSelectionLists();
    }
}

function createChatSession() {
    if (!selectedStudent || !selectedScenario) {
        alert("Please select a student and a scenario.");
        return;
    }

    const newSession = {
        id: Date.now().toString(),
        student: selectedStudent.name,
        scenario: selectedScenario.title,
        timestamp: Date.now(),
        chatLog: [{ sender: "student", text: `Hello! I'm ${selectedStudent.name}, and I'm in the "${selectedScenario.title}" scenario.` }]
    };

    let sessions = JSON.parse(localStorage.getItem("chatSessions")) || [];
    sessions.push(newSession);
    localStorage.setItem("chatSessions", JSON.stringify(sessions));
    localStorage.setItem("activeChatSessionId", newSession.id);

    window.location.href = "chatPage.html";
}

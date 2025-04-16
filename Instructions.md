# Instructions – How to Run/Test the App or Code

## Installation

### 1. Clone the repository:
```bash
git clone https://github.com/yourusername/teacher-training-chatbot.git
cd teacher-training-chatbot
```

### 2. Install the required packages:
```bash
pip install -r requirements.txt
```

### 3. Install Ollama and the required models:
- Download Ollama: https://ollama.com/download

After installing Ollama, run the following commands to install the required models:

```bash
ollama pull llama3.2:3b
ollama pull deepseek-r1:14b
```

---

## Running the Application

### Running the Streamlit App

To start the Streamlit web interface:

```bash
cd teacher-training-chatbot
streamlit run src/app.py
```

The application should open in your browser automatically at [http://localhost:8501](http://localhost:8501)

---

### Using the Command-Line Interface

You can also use the application through the command-line:

```bash
python src/ai/llama_rag.py  # For simple RAG
python src/ai/rag_pipeline.py  # For student profile RAG
```

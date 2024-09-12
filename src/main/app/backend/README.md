# Agent Neo Backend

This is the backend for the Agent Neo project, designed to interact with various Large Language Models (LLMs) and manage conversations stored in a Neo4j graph database. The backend is implemented using FastAPI and supports operations such as retrieving context for questions, rating messages, and logging interactions between users and the LLM.

## Core Components

### 1. **FastAPI Application**
   - The backend is built using FastAPI, a modern web framework for Python that allows for quick development of APIs with automatic generation of OpenAPI documentation.

### 2. **Neo4j Integration**
   - The application interacts with a Neo4j graph database to manage conversations, messages, and other entities. The `GraphReader` and `GraphWriter` classes are used to read from and write to the Neo4j database.
   - Key operations include retrieving conversation history, logging new messages, and rating responses from the LLM.

### 3. **Large Language Model (LLM) Interface**
   - The backend supports multiple LLMs, including OpenAI's GPT models and Google's ChatVertexAI models. The `LLM` class is used to interact with these models, allowing for dynamic selection based on the request.
   - The LLMs are initialized based on environment variables, and different models can be chosen depending on the needs of the conversation.

### 4. **Secret Management**
   - Secrets, such as API keys and other sensitive information, are managed using environment variables and Google Cloud's Secret Manager. The `SecretManager` class abstracts the retrieval of these secrets.

### 5. **Environment Configuration**
   - The application relies on environment variables for configuration, including LLM settings, Neo4j connection details, and API keys. These are typically stored in a `.env` file or managed through a secret manager.

## Running the Backend

### Prerequisites
- **Python 3.10+**: Ensure you have Python installed.
- **Poetry**: Dependency management is handled via Poetry. Install Poetry if you haven't already.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/agent-neo-backend.git
   cd agent-neo-backend
   ```
2. Install dependencies
    ```bash
   poetry install
    ```
3. Install pre-commit hooks
   ```bash
   poetry run pre-commit install
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
5. Run development backend webserver
    ```bash
    poetry run uvicorn main:app --reload
    ```
### Endpoints
- **`/llm`**: Endpoint for interacting with the LLM to generate responses based on a given question and context.
- **`/graph-llm/{conversation_id}`**: Fetches detailed conversation history and related graph data for a specific conversation ID.

## Linting and Formatting
- **Ruff**: Used for linting the codebase.
- **Black**: Used for code formatting.

### Running Linting and Formatting
To lint and format your code, run:
```bash
poetry run ruff check .
poetry run black .

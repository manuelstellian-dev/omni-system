# OMNI Project GEMINI.md

## 🚀 Project Overview

OMNI is an autonomous AI operating environment designed to take a high-level user intent and generate a complete, production-ready software project. It uses a multi-agent architecture to handle different aspects of the software development lifecycle, from initial planning to code generation, verification, and deployment.

**Core Principles:**

*   **Autonomy:** OMNI is designed to work with minimal human intervention. It can take a single command and generate a fully functional application.
*   **Self-Healing:** The system includes a verification and repair loop that automatically detects and fixes errors in the generated code.
*   **Scalability:** The use of a vector database for memory (RAG) allows the system to scale and maintain context for large projects.
*   **Efficiency:** OMNI uses parallel execution for independent tasks, significantly speeding up the code generation process.
*   **Extensibility:** The modular, agent-based architecture makes it easy to add new capabilities and integrations.

**Key Technologies:**

*   **Python:** The core of the OMNI system is written in Python.
*   **Typer:** Used for creating the command-line interface (CLI).
*   **LiteLLM:** A library that provides a unified interface for interacting with various large language models (LLMs).
*   **Pydantic:** Used for data validation and creating structured data models for the project specifications.
*   **Asyncio:** Used for concurrent execution of tasks.
*   **Rich:** For creating beautiful and informative command-line user interfaces.

## 🏗️ Architecture

The OMNI system is composed of several specialized agents, each with a specific role:

*   **Cortex:** The "brain" of the system. It analyzes the user's intent and creates a detailed `ProjectSpec`, which is a structured plan for the entire project. This includes the tech stack, database schema, core features, and a Directed Acyclic Graph (DAG) of tasks.

*   **SwarmAgent:** The primary code generation agent. It takes the `ProjectSpec` from the Cortex and executes the tasks in the DAG to generate the project's code. It uses Retrieval-Augmented Generation (RAG) to maintain context and ensure consistency across the codebase.

*   **ArbiterAgent:** The quality assurance agent. After the `SwarmAgent` generates the code, the `ArbiterAgent` verifies it for correctness and adherence to the project specifications. If it finds issues, it can trigger the `RepairAgent`.

*   **RepairAgent:** The self-healing agent. It takes the error reports from the `ArbiterAgent` and attempts to automatically fix the code. It uses a multi-strategy approach to find the best solution.

*   **DevOpsAgent:** The infrastructure agent. It generates the necessary Infrastructure-as-Code (IaC) files (e.g., `Dockerfile`, `docker-compose.yml`) for the project.

*   **DocEngine:** The documentation agent. It generates documentation for the project based on the `ProjectSpec`.

*   **CompletionAgent:** The "janitor" agent. It generates a `setup.sh` script to automate the project setup process for the user.

*   **MemoryAgent:** The long-term memory of the system. It uses a vector database to store and retrieve information about the project, providing context for the other agents.

## 🛠️ Building and Running

The project is managed using modern Python tooling. Here are the key commands:

*   **Installation:**
    ```bash
    # It's recommended to use a virtual environment
    python -m venv .venv
    source .venv/bin/activate

    # Install dependencies
    pip install -r core/requirements.txt
    ```

*   **Running the application:**
    ```bash
    # The main entry point is core/main.py
    python core/main.py --help
    ```

*   **Running tests:**
    ```bash
    # Run all tests
    pytest

    # Run only unit tests
    pytest -m unit

    # Run only integration tests
    pytest -m integration
    ```

*   **Linting and Formatting:**
    ```bash
    # Format code with black
    black .

    # Sort imports with isort
    isort .

    # Run ruff for linting
    ruff check .

    # Run mypy for type checking
    mypy .
    ```

## 📝 Development Conventions

*   **Code Style:** The project follows the `black` code style with a line length of 100 characters.
*   **Typing:** The project uses `mypy` for static type checking and aims for strict type safety.
*   **Testing:** The project uses `pytest` for testing. Tests are located in the `core/tests` directory and are separated into `unit` and `integration` tests.
*   **Commits:** Commit messages should follow the Conventional Commits specification.
*   **Branching:** The project uses the Gitflow branching model.
*   **Dependencies:** Project dependencies are managed in the `core/requirements.txt` file.

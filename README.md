# api-mocking-engine
AI-powered tool to generate mock APIs from backend source code.
Intelligent API Mocking Engine

An AI-powered, two-tier developer tool that automatically generates functional REST API mock servers directly from raw backend source code.

The Problem

In Agile development, frontend and QA teams are frequently blocked waiting for backend developers to finish and document API endpoints. Traditional mocking tools require tedious manual configuration.

The Solution

This tool eliminates friction by using a Large Language Model (Llama-3 via Hugging Face) to ingest raw Java Spring Boot code, understand the developer's intent, and instantly spin up a dynamic mock server returning realistic JSON data.

System Architecture

The application utilizes a decoupled architecture, allowing the AI parser to scale independently from the high-performance mock server.

The AI Parser (Python / Gradio): A web interface that accepts raw source code. It securely communicates with the Hugging Face Inference API to generate a strict OpenAPI 3.0 JSON specification and realistic mock data.

The Dynamic Mock Server (Java / Spring Boot): A lightweight runtime server that reads the AI-generated JSON contract on startup. It dynamically registers routes at runtime without requiring hardcoded endpoints, intercepting frontend calls and serving the AI-generated mock responses.

Key Features

Zero-Config Mocking: Paste code, get a working API endpoint in seconds.

Intelligent Data Generation: The AI contextually generates realistic dummy data (e.g., recognizing an "email" field and generating "user@example.com").

Automated Documentation: Instantly exports the generated OpenAPI contract as a downloadable PDF for team sharing.

Built-in Security: Implements strict input validation, concurrency queuing, and ephemeral memory management (auto-deleting temporary PDF files).

How to Run Locally

Prerequisites

Python 3.10+

Java 17 & Maven

A free Hugging Face Access Token

1. Start the AI Parser (Frontend/UI)

cd python-parser
pip install -r requirements.txt
# Create a .env file and add: HF_TOKEN=your_token_here
python app.py


The web UI will be available at http://localhost:7860.

2. Start the Java Mock Server (Backend)

Generate a mock API using the web UI first, which creates an openapi-mock.json file in the root directory. Then start the server:

cd java-mock-server
mvn spring-boot:run


The dynamic mock API will be available at http://localhost:8080.

License

This project is open-source and available under the MIT License.

Disclaimer: This tool utilizes LLMs for code analysis. Always review generated API contracts for accuracy before utilizing them in production testing environments.
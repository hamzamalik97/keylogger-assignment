# Controlled Keyboard Event Logging Lab

A Python Flask and Docker-based educational cybersecurity project demonstrating controlled browser keyboard-event capture, HTTP event forwarding, event storage, and dashboard monitoring.

## Overview

This project demonstrates an application-scoped keyboard event logging workflow.

JavaScript captures keyboard events only inside a designated browser test field. The events are sent to a Flask application, forwarded to a Docker-based receiver, timestamped, and stored locally in JSON Lines (JSONL) format.

## Architecture

    Browser Test Page
           |
           | JavaScript Events
           v
    Flask Application
    127.0.0.1:5001
           |
           | HTTP POST
           v
    Docker Event Receiver
    127.0.0.1:5002
           |
           | UTC Timestamp
           v
    JSONL Event Storage
           |
           v
    Dashboard Monitoring

## Technologies

- Python 3
- Flask
- JavaScript
- HTML5
- CSS3
- Docker
- HTTP
- JSON and JSONL

## Project Structure

    keylogger-assignment/
    ├── app.py
    ├── receiver/
    │   ├── Dockerfile
    │   ├── receiver.py
    │   └── requirements.txt
    ├── terminal-victim/
    │   ├── Dockerfile
    │   └── terminal.py
    ├── logs/
    │   └── .gitkeep
    ├── .gitignore
    └── README.md

## Components

### 1. Flask Application

- Serves the browser test page.
- Receives events through the POST /record endpoint.
- Forwards event data to the receiver.
- Retrieves recorded events through the GET /events endpoint.

### 2. Docker Event Receiver

- Receives events through its HTTP API.
- Adds a UTC receipt timestamp.
- Stores events in JSONL format.
- Provides endpoints for event retrieval and health checks.

### 3. Terminal Demonstration

The terminal demonstration records a submitted command when Enter is pressed. It does not capture every terminal keystroke.

### 4. Dashboard

- Displays recorded events.
- Supports searching displayed events.
- Provides a refresh function.
- Shows browser event data retrieved from the receiver.

## Network Configuration

| Component | Address |
|---|---|
| Flask application | 127.0.0.1:5001 |
| Receiver host endpoint | 127.0.0.1:5002 |
| Receiver container port | 5000 |
| Receiver events endpoint | /events |
| Receiver health endpoint | /health |

## Requirements

- Linux or compatible operating system
- Python 3
- pip
- Docker
- Modern web browser

## Running the Project

Start the existing receiver container:

    docker start keylogger-receiver-v2

Start the Flask application:

    cd ~/keylogger-assignment
    .venv/bin/python app.py

Open the dashboard:

    http://127.0.0.1:5001

Use harmless sample text in the designated test field.

## Event Storage

Events are stored locally in:

    logs/events.jsonl

Each line represents a separate JSON event.

Generated logs and backup files are excluded from Git commits to avoid publishing captured test data.

## Security and Ethical Considerations

- Event listeners are restricted to the designated browser test field.
- This project is not a system-wide keylogger.
- Never use it to collect passwords, credentials, or private information.
- Test only on systems and applications you own or are authorized to assess.
- The demonstration uses local HTTP communication and does not implement transport encryption.

## Disclaimer

This project is intended exclusively for educational cybersecurity demonstrations and authorized laboratory testing. Unauthorized monitoring or collection of private information is not supported.

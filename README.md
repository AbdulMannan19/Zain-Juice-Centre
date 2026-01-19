# Juice Cafe Ordering System

A simple web application for a juice ordering cafe with real-time order notifications.

## Project Structure

```
juice-cafe-ordering/
├── backend/
│   └── app.py              # Flask backend server
├── frontend/
│   ├── index.html          # Customer menu page
│   ├── kitchen.html        # Kitchen display page
│   ├── styles.css          # Shared styles
│   ├── menu.js             # Menu page JavaScript
│   ├── kitchen.js          # Kitchen display JavaScript
│   └── assets/             # Static assets (images, logo)
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Setup Instructions

### 1. Create Python Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python backend/app.py
```

The application will be available at:
- Menu Page: http://localhost:5000/
- Kitchen Display: http://localhost:5000/kitchen.html

## Technology Stack

- **Backend**: Python with Flask
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Real-time Communication**: Server-Sent Events (SSE)
- **Data Storage**: In-memory

## Development Status

This is the initial project setup. Features will be implemented incrementally according to the task list.

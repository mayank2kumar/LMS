# 📚 Library Management System
### Live Website link

🌐 [Visit the Live Website](https://mayankkumar.pythonanywhere.com)
## Username and Password for admin Dashboard
username
```
admin
```
password
```
admin
```

A web-based Library Management System built with Flask that allows users to manage books, track availability, and navigate through a clean and responsive interface. It features a dashboard, book registration, and real-time book availability.

🛠 Tech Stack

Backend: Python 3, Flask , Jinja2 templating

Frontend: HTML, CSS (Bootstrap 5)

Database: SQLite

# 🚀 Installation

Follow the steps below to set up and run the project on your local machine:

### 1. Clone the Repository

```bash
git clone https://https://github.com/mayank2kumar/LMS
```
### 2. Change the Working Directory
```bash
cd LMS
```
### 3. Create a New Virtual Environment
``` bash
python -m venv .venv
```
###4. Activate the Virtual Environment
``` bash
.venv\Scripts\activate
```
### 5. Install All Dependencies
``` bash
pip install -r requirements.txt
```
### 6. Run the Application
``` bash
flask run

The app will run on: http://127.0.0.1:5000
```


# 🏗️ Architecture Diagram

```
                    ┌───────────────────────────────┐
                    │         User (Browser)        │
                    └─────────────┬─────────────────┘
                                  │
                                  ▼
                   ┌───────────────────────────────┐
                   │           Flask App           │
                   │       (app.py, routes.py)     │
                   └─────────────┬─────────────────┘
                                  │
        ┌─────────────────────────┼────────────────────────┐
        ▼                         ▼                        ▼
┌─────────────┐         ┌────────────────┐        ┌────────────────────┐
│ Templates/  │◄───────►│  Business Logic│◄─────►│     Static Files    │
│ (Jinja2)    │         │  (routes.py)   │        │ (CSS, JS, images)  │
└─────────────┘         └────────────────┘        └────────────────────┘
                                 │
                                 ▼
                      ┌────────────────────┐
                      │     Models (ORM)   │
                      │   (models.py)      │
                      └────────┬───────────┘
                               ▼
                  ┌────────────────────────────┐
                  │   SQLite (library.db)      │
                  │ SQLAlchemy ORM Interface   │
                  └────────────────────────────┘
```

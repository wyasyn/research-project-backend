# Face Recognition Attendance System Python 3.12

## 📌 Project Overview

This is a **Face Recognition Attendance System** built using Flask and OpenCV. It allows administrators to register users with facial data and mark attendance using face recognition technology. Attendance records can be viewed and exported as Excel files.

## 🏗️ Features

- **User Registration**: Register users with names, emails, unique IDs, and facial images.
- **Face Recognition**: Authenticate users using OpenCV and Face Recognition.
- **Attendance Marking**: Automatically mark attendance once per day when a recognized user logs in.
- **Attendance Reports**: View and download attendance records in Excel format.
- **REST API**: Modular API with user and attendance endpoints.

## 🛠️ Technologies Used

- **Backend**: Flask, Flask-SQLAlchemy, Flask-Migrate
- **Face Recognition**: OpenCV, dlib, face_recognition
- **Database**: SQLite / PostgreSQL
- **Data Processing**: Pandas (for exporting attendance data)

## 📂 Folder Structure

```
face_recognition_attendance/
│── app.py                # Main entry point
│── config.py             # Configuration settings
│── requirements.txt      # Dependencies
│
├── controllers/          # Business logic
│   ├── auth_controller.py       # Handles authentication
│   ├── user_controller.py       # Handles user-related logic
│   ├── attendance_controller.py # Attendance logic
│   ├── face_recognition_controller.py # Face recognition logic
│
├── routes/               # API endpoints
│   ├── auth_routes.py         # Routes for authentication
│   ├── user_routes.py         # Routes for user actions
│   ├── attendance_routes.py   # Routes for attendance management
│   ├── face_routes.py         # Routes for face recognition
│
├── models/               # Database models (SQLAlchemy)
│   ├── user_model.py          # User model
│   ├── attendance_model.py    # Attendance model
│
├── utils/                # Helper functions
│   ├── face_utils.py          # Face recognition helpers
│   ├── image_processing.py    # Image handling functions
│   ├── excel_utils.py         # Export attendance to Excel
│   ├── db_utils.py            # Database utility functions
│
├── migrations/           # Database migrations
│── static/               # Static files
│── templates/            # HTML templates
```

## ⚡ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/wyasyn/research-project-backend.git
cd research-project-backend
```

### 2️⃣ Setup Virtual Environment

#### For Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

#### For macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Setup the Database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5️⃣ Run the Application

```bash
python app.py
```

### How to create a secret key

```bash
openssl rand -base64 32
```

Access the API at: `http://127.0.0.1:5000/`

## 📌 API Endpoints

### 👤 User Management

| Method | Endpoint          | Description         |
| ------ | ----------------- | ------------------- |
| POST   | `/users/register` | Register a new user |

### 📅 Attendance Management

| Method | Endpoint             | Description                |
| ------ | -------------------- | -------------------------- |
| POST   | `/attendance/mark`   | Mark attendance            |
| GET    | `/attendance/export` | Export attendance to Excel |

## 📜 License

This project is licensed under the MIT License.

---

🚀 **Developed by Yasin Walum & Team** 🚀

# Placement Portal Application

A role-based **Flask web application** for managing campus placement activities including companies, students, placement drives, and job applications.
 
**Deploy link**: https://placement-portal-vsf8.onrender.com/

---

# Features

## Admin Features
- Dashboard showing total **companies, students, drives, and applications**
- Admin account **auto-created programmatically**
- Approve / Reject company registrations
- Approve placement drives created by companies
- Blacklist companies or students
- Search companies by **name**
- Search students by **name, ID, or qualification**
- View all placement drives and student applications
- View student resumes

## Company Features
- Register and login after **admin approval**
- Create new placement drives
- Edit, delete, or close drives
- View student applications
- Update application status:
  - Shortlisted
  - Selected
  - Rejected
- View student resume details

## Student Features
- Register and login
- View approved placement drives
- Apply for placement drives
- View application status
- Edit profile and upload resume
- View application history

---

# Tech Stack

### Backend
- Flask (Python Web Framework)
- Flask Session (Authentication)
- Flask-SQLAlchemy (ORM)

### Database
- SQLite

### Frontend
- HTML5
- Bootstrap 5
- Jinja2 Templates
- CSS

---

# Project Structure
```text
📦 JobFinder
│
├── 📂 backend
│   ├── controllers.py
│   └── models.py
│
├── 📂 instance
│   └── jobfinder.sqlite3
│
├── 📂 static
│   ├── 📂 resumes
│   └── style.css
│
├── 📂 templates
│   │
│   ├── 📂 Admin
│   │   ├── admin_base.html
│   │   ├── admin_home.html
│   │   ├── ongoing_drives.html
│   │   ├── student_applications.html
│   │   └── student_details.html
│   │
│   ├── 📂 Company
│   │   ├── add_drive.html
│   │   ├── company_base.html
│   │   ├── company_home.html
│   │   ├── edit_drive.html
│   │   ├── see_drive_student.html
│   │   └── update_student_application.html
│   │
│   ├── 📂 Student
│   │   ├── company_details.html
│   │   ├── edit_profile.html
│   │   ├── history.html
│   │   ├── student_base.html
│   │   └── student_home.html
│   │
│   ├── company_register.html
│   ├── index_base.html
│   ├── index.html
│   ├── signup.html
│   └── view_drive.html
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```
---

# Database Models

- User
- Student_Profile
- Company_Profile
- Placement_Drive
- Application

---
## Setup Instructions

### 1. Clone Repository

```bash
git clone <your-repository-url>
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The application will run locally on:

http://127.0.0.1:5000/

---

# Key Functionalities

- Prevent **duplicate applications**
- Only **approved companies can create drives**
- Students see **only approved placement drives**
- Role-based access control

---

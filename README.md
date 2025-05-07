# PROJECT_PMB_SISWA (Student Admission System)

A web-based student admission system built with Flask and SQLite.

**Developer:** Rafa Satria Isyo Pratama

## 🚀 Features

### User Features
- User registration and authentication
- Student admission form submission
- Real-time application status tracking
- Profile management
- Form data validation

### Admin Features
- Complete application management
- Accept/Reject applications
- View detailed student information
- Application status updates
- Student data management

## 🛠️ Technology Stack

- **Backend:** Python Flask
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Frontend:** 
  - HTML5
  - CSS3
  - JavaScript
  - Bootstrap 5
- **Authentication:** Flask-Login
- **Forms:** Flask-WTF
- **Database Migrations:** Flask-Migrate

## 📋 Prerequisites

- Python 3.8+
- pip
- virtualenv

## 🔧 Installation & Setup

1. **Clone the repository**
```bash
git clone https://github.com/liavin5115/PPDB_PROJECT_RPL.git
cd PPDB_PROJECT_RPL
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Initialize the database**
```bash
flask db upgrade
```

5. **Create an admin user**
```bash
flask create-admin admin yourpassword
```

6. **Run the application**
```bash
flask run
```

Visit `http://localhost:5000` in your browser

## 📁 Project Structure
```
PROJECT_PMB_SISWA/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models
│   ├── cli.py              # CLI commands
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py         # Authentication routes
│   │   └── main.py         # Main application routes
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── script.js
│   └── templates/
│       ├── base.html
│       ├── landing_page.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard_user.html
│       └── dashboard_admin.html
├── migrations/              # Database migrations
├── config.py               # Application configuration
├── requirements.txt        # Project dependencies
└── run.py                 # Application entry point
```


## 👥 User Roles & Permissions

### Student/User
- Register and login
- Submit admission forms
- Track application status
- View profile information

### Admin
- Manage student applications
- Accept/Reject applications
- View detailed student information
- Access admin dashboard

## 💻 Development

1. **Database Migrations**
```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

2. **Creating Admin User**
```bash
flask create-admin admin password123
```

## 📧 Contact & Support

**Developer:** Rafa Satria Isyo Pratama
- GitHub: [\[Your GitHub\]](https://github.com/liavin5115)
- Email: rafa.satria.isyo.pratama.2008@gmail.com


## 📝 License

This project is licensed under the MIT License.

---
Made with ❤️ by Rafa Satria Isyo Pratama

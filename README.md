# SecureCloud

SecureCloud is a secure cloud file storage web application built with Flask and AWS S3.

The application allows users to create accounts, securely log in, upload files, store them in cloud storage, download them, and generate sharing links.

It also includes an administrator system for managing users, files, and system activity.

---

## Features

- User registration and login
- Secure password hashing
- Session-based authentication
- File upload
- File download
- File deletion
- AWS S3 cloud storage
- File encryption
- Secure file sharing
- Share link generation
- Stop sharing files
- File search
- Admin account setup
- Admin dashboard
- User management
- File management
- Activity logging
- Environment-based secret configuration
- Responsive dark-themed interface

---

## Technologies Used

### Backend

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Boto3
- Cryptography
- Python-dotenv

### Frontend

- HTML5
- CSS3
- JavaScript
- Jinja2 templates

### Cloud Storage

- Amazon Web Services S3

---

## Project Structure

```text
securecloud/
│
├── app.py
├── .gitignore
├── README.md
│
└── templates/
    ├── Admin.html
    ├── Files.html
    ├── Share.html
    ├── admin_setup.html
    ├── dashboard.html
    ├── login.html
    └── register.html
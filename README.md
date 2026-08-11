# SecureCloud

SecureCloud is a cloud-based file storage web application that I developed using Python Flask and Amazon S3.

The main idea behind the project is to allow users to securely create an account, log in, upload files, store them in cloud storage, download them when needed, and share files using generated links.

The project also includes an administrator system where an authorized administrator can manage users, files, and view system activity.

---

## What SecureCloud Can Do

The application includes the following features:

- User registration
- User login and logout
- Secure password hashing
- File upload
- File download
- File deletion
- File search
- AWS S3 cloud storage
- File encryption
- File sharing through generated links
- Ability to stop sharing files
- Administrator setup
- Admin dashboard
- User management
- File management
- Activity logging
- Environment-based configuration
- Responsive dark-themed interface

---

## Technologies Used

I used the following technologies to build the project:

### Backend

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Boto3
- Cryptography
- Python-dotenv

### Frontend

- HTML
- CSS
- JavaScript
- Jinja2

### Cloud Storage

- Amazon S3

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
```

---

## How the Application Works

A new user can create an account from the registration page.

After registering, the user can log in using their username and password.

Once logged in, the user is taken to the dashboard where they can manage their files.

The main file operations are:

- Uploading files
- Viewing files
- Downloading files
- Deleting files
- Searching for files
- Sharing files

Files are stored using Amazon S3 so that the application can use cloud storage instead of depending completely on the local computer.

---

## File Sharing

SecureCloud allows users to create a sharing link for a file.

The user can copy the generated link and share it with someone else.

The application does not directly expose the S3 bucket to users. File access is handled through the application.

Users can also stop sharing a file when they no longer want the sharing link to work.

---

## Admin Panel

The project also has an administrator system.

A registered user can be made an administrator through the admin setup process.

After becoming an administrator, the user can access the admin panel.

The admin panel provides options for managing and viewing:

- Users
- Files
- User roles
- System activity

The administrator setup code is stored outside the main source code so that it is not directly exposed in the application files.

---

## Security

Security was an important part of this project.

Some of the security measures used in SecureCloud are:

- Password hashing
- Login authentication
- Session-based access
- Protected admin access
- File encryption
- Private AWS S3 storage
- Environment variables for sensitive configuration
- Protected file access
- GitHub protection for secret files

Sensitive values such as secret keys, administrator setup codes, and AWS credentials are stored in a `.env` file.

The `.env` file is not uploaded to GitHub.

---

## Environment Variables

Before running the application, create a `.env` file in the main project folder.

It should contain your own configuration values.

For example:

```env
FLASK_SECRET_KEY=your-secret-key
ADMIN_SETUP_CODE=your-admin-setup-code
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=your-aws-region
S3_BUCKET=your-s3-bucket-name
```

These are only example values.

Do not put your real passwords, AWS credentials, secret keys, or admin setup code in this README or on GitHub.

---

## How to Run the Project

First, clone the repository:

```bash
git clone https://github.com/rushikeshpatil7667-bot/securecloud.git
```

Open the project folder:

```bash
cd securecloud
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
pip install flask flask-sqlalchemy boto3 cryptography python-dotenv
```

Create your `.env` file and add your configuration.

After that, start the application:

```powershell
python app.py
```

The application can normally be opened at:

```text
http://127.0.0.1:5000
```

---

## AWS S3

SecureCloud uses Amazon S3 for storing uploaded files.

The application needs the AWS credentials, AWS region, and S3 bucket name through environment variables.

The S3 bucket should be kept private.

AWS credentials should never be written directly inside `app.py` or uploaded to GitHub.

---

## GitHub and Sensitive Files

The project uses a `.gitignore` file to prevent sensitive and unnecessary files from being uploaded to GitHub.

Files such as these are kept out of the repository:

```text
.env
.venv/
__pycache__/
*.pyc
instance/
uploads/
storage/
*.db
```

This helps keep private configuration, local databases, uploaded files, and development files away from the public repository.

---

## Future Improvements

There are several things that could be added to the project in the future:

- Password reset
- Email verification
- Two-factor authentication
- Expiring file sharing links
- Better file previews
- File upload progress
- More admin controls
- More detailed activity logs
- Automated security testing
- Deployment to a cloud server
- Production database support

---

## Project Purpose

I developed SecureCloud as an internship project to gain practical experience with Flask, databases, cloud storage, authentication, encryption, and web application security.

The project helped me understand how a web application can connect with cloud storage and how sensitive configuration should be kept separate from the application source code.

---

## Author

Developed as an internship project.

**SecureCloud - Secure and private cloud file storage.**
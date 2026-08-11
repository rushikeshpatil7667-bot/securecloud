from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    abort
)

from flask_sqlalchemy import SQLAlchemy

from flask_login import (
    UserMixin,
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

from cryptography.fernet import (
    Fernet,
    InvalidToken
)

from dotenv import load_dotenv

from datetime import datetime
from io import BytesIO

import os
import secrets
import boto3


load_dotenv()


app = Flask(__name__)


app.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET_KEY"
)

if not app.config["SECRET_KEY"]:
    raise RuntimeError(
        "FLASK_SECRET_KEY is not set."
    )


app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///database.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)


S3_BUCKET = os.environ.get(
    "S3_BUCKET",
    "rushi-secure-cloud-storage-2026"
)

S3_REGION = os.environ.get(
    "AWS_REGION",
    "ap-south-1"
)


s3 = boto3.client(
    "s3",
    region_name=S3_REGION
)


ADMIN_SETUP_CODE = os.environ.get(
    "ADMIN_SETUP_CODE"
)

if not ADMIN_SETUP_CODE:
    raise RuntimeError(
        "ADMIN_SETUP_CODE is not set."
    )


login_manager = LoginManager(app)

login_manager.login_view = "login"


UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    "instance",
    exist_ok=True
)


KEY_FILE = os.path.join(
    "instance",
    "secret.key"
)


if not os.path.exists(KEY_FILE):

    with open(
        KEY_FILE,
        "wb"
    ) as key_file:

        key_file.write(
            Fernet.generate_key()
        )


with open(
    KEY_FILE,
    "rb"
) as key_file:

    encryption_key = key_file.read()


cipher = Fernet(
    encryption_key
)


class User(
    db.Model,
    UserMixin
):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(150),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="user",
        nullable=False
    )


class File(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    filename = db.Column(
        db.String(200),
        nullable=False
    )

    owner_id = db.Column(
        db.Integer,
        nullable=False
    )

    file_size = db.Column(
        db.Integer,
        nullable=True
    )

    file_type = db.Column(
        db.String(100),
        nullable=True
    )

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    encrypted = db.Column(
        db.Boolean,
        default=True
    )


class FileShare(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    file_id = db.Column(
        db.Integer,
        nullable=False
    )

    owner_id = db.Column(
        db.Integer,
        nullable=False
    )

    share_token = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    active = db.Column(
        db.Boolean,
        default=True
    )


class ActivityLog(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(150),
        nullable=False
    )

    action = db.Column(
        db.String(50),
        nullable=False
    )

    filename = db.Column(
        db.String(200),
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(
        int(user_id)
    )


with app.app_context():

    db.create_all()

    user_columns = db.session.execute(
        db.text(
            "PRAGMA table_info(user)"
        )
    ).fetchall()

    user_column_names = [
        column[1]
        for column in user_columns
    ]

    if "role" not in user_column_names:

        db.session.execute(
            db.text(
                "ALTER TABLE user "
                "ADD COLUMN role VARCHAR(20) "
                "DEFAULT 'user'"
            )
        )

    db.session.execute(
        db.text(
            "UPDATE user SET role = 'user' "
            "WHERE role IS NULL"
        )
    )

    file_columns = db.session.execute(
        db.text(
            "PRAGMA table_info(file)"
        )
    ).fetchall()

    file_column_names = [
        column[1]
        for column in file_columns
    ]

    if "file_size" not in file_column_names:

        db.session.execute(
            db.text(
                "ALTER TABLE file "
                "ADD COLUMN file_size INTEGER"
            )
        )

    if "file_type" not in file_column_names:

        db.session.execute(
            db.text(
                "ALTER TABLE file "
                "ADD COLUMN file_type VARCHAR(100)"
            )
        )

    if "uploaded_at" not in file_column_names:

        db.session.execute(
            db.text(
                "ALTER TABLE file "
                "ADD COLUMN uploaded_at DATETIME"
            )
        )

    if "encrypted" not in file_column_names:

        db.session.execute(
            db.text(
                "ALTER TABLE file "
                "ADD COLUMN encrypted BOOLEAN "
                "DEFAULT 1"
            )
        )

    db.session.commit()


@app.route("/")
def home():

    return redirect(
        url_for("login")
    )


@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if not username or not password:

            return (
                "Username and password are required."
            ), 400

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:

            return (
                "Username already exists. "
                "Please choose another one."
            ), 409

        hashed_password = (
            generate_password_hash(
                password,
                method="pbkdf2:sha256"
            )
        )

        new_user = User(
            username=username,
            password=hashed_password,
            role="user"
        )

        db.session.add(
            new_user
        )

        db.session.commit()

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect(
                url_for("dashboard")
            )

        return (
            "Invalid username or password. "
            "Please try again."
        ), 401

    return render_template(
        "login.html"
    )


@app.route(
    "/admin-setup",
    methods=["GET", "POST"]
)
def admin_setup():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        setup_code = request.form.get(
            "setup_code",
            ""
        )

        if not setup_code:

            return (
                "Admin setup code is required."
            ), 400

        if setup_code != ADMIN_SETUP_CODE:

            return (
                "Invalid admin setup code."
            ), 403

        user = User.query.filter_by(
            username=username
        ).first()

        if not user:

            return (
                "User not found. "
                "Register the account first."
            ), 404

        user.role = "admin"

        db.session.commit()

        return (
            "Admin account created successfully. "
            "You can now login with this account."
        )

    return render_template(
        "admin_setup.html"
    )


@app.route("/dashboard")
@login_required
def dashboard():

    files = File.query.filter_by(
        owner_id=current_user.id
    ).order_by(
        File.uploaded_at.desc()
    ).all()

    logs = ActivityLog.query.filter_by(
        username=current_user.username
    ).order_by(
        ActivityLog.timestamp.desc()
    ).limit(10).all()

    return render_template(
        "dashboard.html",
        files=files,
        logs=logs,
        username=current_user.username
    )


@app.route("/files")
@login_required
def my_files():

    files = File.query.filter_by(
        owner_id=current_user.id
    ).order_by(
        File.uploaded_at.desc()
    ).all()

    shares = FileShare.query.filter_by(
        owner_id=current_user.id,
        active=True
    ).all()

    share_links = {}

    for share in shares:

        share_links[
            share.file_id
        ] = url_for(
            "shared_file",
            token=share.share_token,
            _external=True
        )

    return render_template(
        "files.html",
        files=files,
        shares=shares,
        share_links=share_links,
        username=current_user.username
    )


@app.route("/admin")
@login_required
def admin_panel():

    if current_user.role != "admin":

        return (
            "Access denied. "
            "Administrator permission is required."
        ), 403

    users = User.query.order_by(
        User.id.asc()
    ).all()

    files = File.query.order_by(
        File.uploaded_at.desc()
    ).all()

    logs = ActivityLog.query.order_by(
        ActivityLog.timestamp.desc()
    ).limit(50).all()

    return render_template(
        "admin.html",
        users=users,
        files=files,
        logs=logs
    )


@app.route(
    "/upload",
    methods=["POST"]
)
@login_required
def upload_file():

    files = request.files.getlist(
        "files"
    )

    if not files:

        return (
            "No files selected."
        ), 400

    uploaded_count = 0

    for file in files:

        if not file or not file.filename:
            continue

        filename = secure_filename(
            file.filename
        )

        if not filename:
            continue

        original_data = file.read()

        if not original_data:
            continue

        old_file = File.query.filter_by(
            owner_id=current_user.id,
            filename=filename
        ).first()

        if old_file:

            name, extension = os.path.splitext(
                filename
            )

            filename = (
                name
                + "_"
                + datetime.now().strftime(
                    "%Y%m%d%H%M%S"
                )
                + extension
            )

        encrypted_data = cipher.encrypt(
            original_data
        )

        s3_key = (
            f"user_{current_user.id}/"
            f"{filename}"
        )

        try:

            s3.upload_fileobj(
                BytesIO(encrypted_data),
                S3_BUCKET,
                s3_key
            )

        except Exception:

            return (
                "The file could not be uploaded."
            ), 500

        new_file = File(
            filename=filename,
            owner_id=current_user.id,
            file_size=len(
                original_data
            ),
            file_type=file.content_type,
            encrypted=True
        )

        db.session.add(
            new_file
        )

        activity = ActivityLog(
            username=current_user.username,
            action="UPLOAD",
            filename=filename
        )

        db.session.add(
            activity
        )

        uploaded_count += 1

    db.session.commit()

    if uploaded_count == 0:

        return (
            "No valid files were uploaded."
        ), 400

    return redirect(
        url_for("dashboard")
    )


@app.route(
    "/download/<int:file_id>"
)
@login_required
def download_file(file_id):

    file = File.query.filter_by(
        id=file_id,
        owner_id=current_user.id
    ).first_or_404()

    s3_key = (
        f"user_{current_user.id}/"
        f"{file.filename}"
    )

    try:

        response = s3.get_object(
            Bucket=S3_BUCKET,
            Key=s3_key
        )

        encrypted_data = (
            response["Body"].read()
        )

        try:

            original_data = cipher.decrypt(
                encrypted_data
            )

        except InvalidToken:

            return (
                "Unable to decrypt this file."
            ), 500

        activity = ActivityLog(
            username=current_user.username,
            action="DOWNLOAD",
            filename=file.filename
        )

        db.session.add(
            activity
        )

        db.session.commit()

        return send_file(
            BytesIO(original_data),
            as_attachment=True,
            download_name=file.filename,
            mimetype=(
                file.file_type
                or "application/octet-stream"
            )
        )

    except Exception:

        return (
            "The file could not be downloaded."
        ), 500


@app.route(
    "/share/<int:file_id>",
    methods=["POST"]
)
@login_required
def share_file(file_id):

    file = File.query.filter_by(
        id=file_id,
        owner_id=current_user.id
    ).first_or_404()

    existing_share = FileShare.query.filter_by(
        file_id=file.id,
        owner_id=current_user.id,
        active=True
    ).first()

    if existing_share:

        share_token = (
            existing_share.share_token
        )

    else:

        share_token = secrets.token_urlsafe(
            32
        )

        new_share = FileShare(
            file_id=file.id,
            owner_id=current_user.id,
            share_token=share_token,
            active=True
        )

        db.session.add(
            new_share
        )

        activity = ActivityLog(
            username=current_user.username,
            action="SHARE",
            filename=file.filename
        )

        db.session.add(
            activity
        )

        db.session.commit()

    share_link = url_for(
        "shared_file",
        token=share_token,
        _external=True
    )

    return render_template(
        "share.html",
        file=file,
        share_link=share_link
    )


@app.route(
    "/shared/<token>"
)
def shared_file(token):

    share = FileShare.query.filter_by(
        share_token=token,
        active=True
    ).first()

    if not share:

        abort(404)

    file = File.query.filter_by(
        id=share.file_id
    ).first()

    if not file:

        abort(404)

    s3_key = (
        f"user_{share.owner_id}/"
        f"{file.filename}"
    )

    try:

        response = s3.get_object(
            Bucket=S3_BUCKET,
            Key=s3_key
        )

        encrypted_data = (
            response["Body"].read()
        )

        try:

            original_data = cipher.decrypt(
                encrypted_data
            )

        except InvalidToken:

            return (
                "Unable to decrypt this shared file."
            ), 500

        activity = ActivityLog(
            username="Shared Link",
            action="SHARED DOWNLOAD",
            filename=file.filename
        )

        db.session.add(
            activity
        )

        db.session.commit()

        return send_file(
            BytesIO(original_data),
            as_attachment=True,
            download_name=file.filename,
            mimetype=(
                file.file_type
                or "application/octet-stream"
            )
        )

    except Exception:

        return (
            "The shared file could not be downloaded."
        ), 500


@app.route(
    "/unshare/<int:file_id>",
    methods=["POST"]
)
@login_required
def unshare_file(file_id):

    file = File.query.filter_by(
        id=file_id,
        owner_id=current_user.id
    ).first_or_404()

    share = FileShare.query.filter_by(
        file_id=file.id,
        owner_id=current_user.id,
        active=True
    ).first()

    if share:

        share.active = False

        activity = ActivityLog(
            username=current_user.username,
            action="UNSHARE",
            filename=file.filename
        )

        db.session.add(
            activity
        )

        db.session.commit()

    return redirect(
        url_for("my_files")
    )


@app.route(
    "/delete/<int:file_id>",
    methods=["POST", "GET"]
)
@login_required
def delete_file(file_id):

    file = File.query.filter_by(
        id=file_id,
        owner_id=current_user.id
    ).first_or_404()

    s3_key = (
        f"user_{current_user.id}/"
        f"{file.filename}"
    )

    try:

        s3.delete_object(
            Bucket=S3_BUCKET,
            Key=s3_key
        )

    except Exception:

        return (
            "The file could not be deleted."
        ), 500

    shares = FileShare.query.filter_by(
        file_id=file.id,
        owner_id=current_user.id
    ).all()

    for share in shares:

        share.active = False

    activity = ActivityLog(
        username=current_user.username,
        action="DELETE",
        filename=file.filename
    )

    db.session.add(
        activity
    )

    db.session.delete(
        file
    )

    db.session.commit()

    return redirect(
        url_for("dashboard")
    )


@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("login")
    )


if __name__ == "__main__":

    app.run(
        debug=True
    )
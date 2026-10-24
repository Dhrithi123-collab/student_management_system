import os
import sqlite3
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        DATABASE=os.environ.get(
            "DATABASE",
            str(Path(app.root_path) / "students.db"),
        ),
        TESTING=False,
    )

    if test_config:
        app.config.update(test_config)

    def connect_db():
        connection = sqlite3.connect(app.config["DATABASE"])
        connection.row_factory = sqlite3.Row
        return connection

    def init_db():
        with connect_db() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL
                        CHECK(role IN ('admin', 'staff'))
                )
                """
            )

            db.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    course TEXT NOT NULL
                )
                """
            )

            # Demo accounts. Change these before real deployment.
            for username, password, role in [
                ("admin", "Admin123!", "admin"),
                ("staff", "Staff123!", "staff"),
            ]:
                db.execute(
                    """
                    INSERT OR IGNORE INTO users
                        (username, password_hash, role)
                    VALUES (?, ?, ?)
                    """,
                    (
                        username,
                        generate_password_hash(password),
                        role,
                    ),
                )

    with app.app_context():
        init_db()

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                if request.path.startswith("/api/"):
                    return jsonify({"error": "Authentication required"}), 401

                return redirect(url_for("login"))

            return view(*args, **kwargs)

        return wrapped

    def admin_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if session.get("role") != "admin":
                return jsonify({"error": "Admin access required"}), 403

            return view(*args, **kwargs)

        return wrapped

    def student_data():
        data = request.get_json(silent=True) or request.form

        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip().lower()
        course = str(data.get("course", "")).strip()

        if not name or not email or not course:
            return None

        if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            return None

        return name, email, course

    @app.route("/")
    def index():
        if "user_id" not in session:
            return redirect(url_for("login"))

        return redirect(url_for("students_page"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            with connect_db() as db:
                user = db.execute(
                    "SELECT * FROM users WHERE username = ?",
                    (username,),
                ).fetchone()

            if user and check_password_hash(
                user["password_hash"], password
            ):
                session.clear()
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["role"] = user["role"]

                return redirect(url_for("students_page"))

            return render_template(
                "login.html",
                error="Invalid username or password",
            ), 401

        return render_template("login.html")

    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/students")
    @login_required
    def students_page():
        with connect_db() as db:
            students = db.execute(
                "SELECT * FROM students ORDER BY id DESC"
            ).fetchall()

        return render_template(
            "students.html",
            students=students,
            username=session["username"],
            role=session["role"],
        )

    @app.route("/api/students", methods=["GET"])
    @login_required
    def list_students():
        with connect_db() as db:
            rows = db.execute(
                "SELECT * FROM students ORDER BY id"
            ).fetchall()

        return jsonify([dict(row) for row in rows])

    @app.route("/api/students", methods=["POST"])
    @login_required
    def add_student():
        data = student_data()

        if not data:
            return jsonify({"error": "Invalid student data"}), 400

        try:
            with connect_db() as db:
                cursor = db.execute(
                    """
                    INSERT INTO students (name, email, course)
                    VALUES (?, ?, ?)
                    """,
                    data,
                )
                student_id = cursor.lastrowid

        except sqlite3.IntegrityError:
            return jsonify({"error": "Email already exists"}), 409

        return jsonify({"id": student_id, "message": "Student added"}), 201

    @app.route("/api/students/<int:student_id>", methods=["PUT"])
    @login_required
    def edit_student(student_id):
        data = student_data()

        if not data:
            return jsonify({"error": "Invalid student data"}), 400

        try:
            with connect_db() as db:
                cursor = db.execute(
                    """
                    UPDATE students
                    SET name = ?, email = ?, course = ?
                    WHERE id = ?
                    """,
                    (*data, student_id),
                )

                if cursor.rowcount == 0:
                    return jsonify({"error": "Student not found"}), 404

        except sqlite3.IntegrityError:
            return jsonify({"error": "Email already exists"}), 409

        return jsonify({"message": "Student updated"})

    @app.route("/api/students/<int:student_id>", methods=["DELETE"])
    @login_required
    @admin_required
    def delete_student(student_id):
        with connect_db() as db:
            cursor = db.execute(
                "DELETE FROM students WHERE id = ?",
                (student_id,),
            )

            if cursor.rowcount == 0:
                return jsonify({"error": "Student not found"}), 404

        return jsonify({"message": "Student deleted"})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
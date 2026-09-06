from flask import Flask, render_template, request, redirect, session
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"
db = SQL("sqlite:///todo.db")

@app.route("/")
def index():

    if "user_id" not in session:
        return redirect("/login")

    search = request.args.get("search", "")

    tasks = db.execute(
        """
        SELECT * FROM tasks
        WHERE user_id = ?
        AND (title LIKE ? OR description LIKE ?)
        ORDER BY completed, id DESC
        """,
        session["user_id"],
        "%" + search + "%",
        "%" + search + "%"
    )

    total = db.execute(
        "SELECT COUNT(*) AS count FROM tasks WHERE user_id = ?",
        session["user_id"]
    )[0]["count"]

    completed = db.execute(
        "SELECT COUNT(*) AS count FROM tasks WHERE user_id = ? AND completed = 1",
        session["user_id"]
    )[0]["count"]

    pending = total - completed

    return render_template(
        "index.html",
        tasks=tasks,
        search=search,
        total=total,
        completed=completed,
        pending=pending
    )


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return "Must provide username"

        if not password:
            return "Must provide password"

        if password != confirmation:
            return "Passwords do not match"

        hash = generate_password_hash(password)

        try:
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                username,
                hash
            )
        except:
            return "Username already exists"

        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return "Must provide username"
        if not password:
            return "Must provide password"
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?",
            username
        )
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return "Invalid username or password"
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()

    return redirect("/")


@app.route("/add", methods=["GET", "POST"])
def add():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")
        priority = request.form.get("priority")
        deadline = request.form.get("deadline")

        if not title:
            return "Must provide a title"

        db.execute(
            "INSERT INTO tasks (user_id, title, description, priority, deadline) VALUES (?, ?, ?, ?, ?)",
            session["user_id"],
            title,
            description,
            priority,
            deadline
        )

        return redirect("/")

    else:
        return render_template("add.html")


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id):

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":


        title = request.form.get("title")
        description = request.form.get("description")
        priority = request.form.get("priority")
        deadline = request.form.get("deadline")

        if not title:
            return "Must provide a title"
        db.execute(
            "UPDATE tasks SET title = ?, description = ?, priority = ?, deadline = ? WHERE id = ? AND user_id = ?",
            title,
            description,
            priority,
            deadline,
            task_id,
            session["user_id"]
        )

        return redirect("/")
    else:
        rows = db.execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            task_id,
            session["user_id"]
        )
        if len(rows) != 1:
            return "Task not found"
        return render_template("edit.html", task=rows[0])





@app.route("/complete/<int:task_id>", methods=["POST"])
def complete(task_id):

    if "user_id" not in session:
        return redirect("/login")

    db.execute(
        "UPDATE tasks SET completed = 1 WHERE id = ? AND user_id = ?",
        task_id,
        session["user_id"]
    )
    return redirect("/")


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    if "user_id" not in session:
        return redirect("/login")
    db.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        task_id,
        session["user_id"]
    )
    return redirect("/")

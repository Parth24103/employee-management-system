from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "beginner-project-secret-key"

DATABASE = "employees.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            position TEXT NOT NULL,
            salary REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    search = request.args.get("search", "").strip()
    conn = get_db_connection()

    if search:
        employees = conn.execute("""
            SELECT * FROM employees
            WHERE name LIKE ? OR email LIKE ?
               OR department LIKE ? OR position LIKE ?
            ORDER BY id DESC
        """, (f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%")).fetchall()
    else:
        employees = conn.execute(
            "SELECT * FROM employees ORDER BY id DESC"
        ).fetchall()

    conn.close()
    return render_template("index.html", employees=employees, search=search)


@app.route("/add", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        department = request.form["department"].strip()
        position = request.form["position"].strip()
        salary = request.form["salary"].strip()

        if not all([name, email, department, position, salary]):
            flash("Please fill in all fields.", "danger")
            return render_template("add_employee.html")

        try:
            salary = float(salary)
        except ValueError:
            flash("Salary must be a number.", "danger")
            return render_template("add_employee.html")

        conn = get_db_connection()
        conn.execute("""
            INSERT INTO employees (name, email, department, position, salary)
            VALUES (?, ?, ?, ?, ?)
        """, (name, email, department, position, salary))
        conn.commit()
        conn.close()

        flash("Employee added successfully.", "success")
        return redirect(url_for("index"))

    return render_template("add_employee.html")


@app.route("/edit/<int:employee_id>", methods=["GET", "POST"])
def edit_employee(employee_id):
    conn = get_db_connection()
    employee = conn.execute(
        "SELECT * FROM employees WHERE id = ?", (employee_id,)
    ).fetchone()

    if employee is None:
        conn.close()
        return "Employee not found", 404

    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        department = request.form["department"].strip()
        position = request.form["position"].strip()
        salary = request.form["salary"].strip()

        try:
            salary = float(salary)
        except ValueError:
            flash("Salary must be a number.", "danger")
            conn.close()
            return render_template("edit_employee.html", employee=employee)

        conn.execute("""
            UPDATE employees
            SET name = ?, email = ?, department = ?, position = ?, salary = ?
            WHERE id = ?
        """, (name, email, department, position, salary, employee_id))
        conn.commit()
        conn.close()

        flash("Employee updated successfully.", "success")
        return redirect(url_for("index"))

    conn.close()
    return render_template("edit_employee.html", employee=employee)


@app.route("/delete/<int:employee_id>", methods=["POST"])
def delete_employee(employee_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
    conn.commit()
    conn.close()

    flash("Employee deleted successfully.", "success")
    return redirect(url_for("index"))


@app.route("/employee/<int:employee_id>")
def employee_details(employee_id):
    conn = get_db_connection()
    employee = conn.execute(
        "SELECT * FROM employees WHERE id = ?", (employee_id,)
    ).fetchone()
    conn.close()

    if employee is None:
        return "Employee not found", 404

    return render_template("employee_details.html", employee=employee)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

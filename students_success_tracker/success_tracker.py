import sys
import os
import typer
from rich.console import Console
from rich.table import Table
from db import init_db, add_student, get_students, find_students_by_major, update_student_gpa, delete_student

console = Console()
app = typer.Typer()


def check_venv():
    if sys.prefix == sys.base_prefix and not os.environ.get("VIRTUAL_ENV"):
        raise RuntimeError(
            "Virtual environment not active. "
            "Activate it with: source .venv/bin/activate"
        )


@app.command(name="init-db")
def init_db_cmd(seed_demo: bool = typer.Option(False)):
    init_db(seed_demo)
    console.print("[green]Database initialized successfully.[/green]")


@app.command()
def add(name: str = typer.Option(...), email: str = typer.Option(...),
        major: str = typer.Option(...), gpa: float = typer.Option(...),
        status: str = typer.Option("active")):
    try:
        student_id = add_student(name, email, major, gpa, status)
        console.print(f"[green]Student added with ID {student_id}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to add student: {e}[/red]")


@app.command()
def list(status: str = typer.Option(None)):
    students = get_students(status)
    if not students:
        console.print("[yellow]No students found.[/yellow]")
        return
    table = Table(title="Students")
    for col in ["id", "name", "email", "major", "gpa", "status", "last_updated"]:
        table.add_column(col.capitalize())
    for s in students:
        table.add_row(*(str(s[col]) for col in ["id", "name", "email", "major", "gpa", "status", "last_updated"]))
    console.print(table)


@app.command()
def find_major(major: str):
    students = find_students_by_major(major)
    if not students:
        console.print(f"[yellow]No students found for major: {major}[/yellow]")
        return
    table = Table(title=f"Students in {major}")
    for col in ["id", "name", "email", "gpa", "status", "last_updated"]:
        table.add_column(col.capitalize())
    for s in students:
        table.add_row(*(str(s[col]) for col in ["id", "name", "email", "gpa", "status", "last_updated"]))
    console.print(table)


@app.command()
def update_gpa(student_id: int = typer.Option(...), gpa: float = typer.Option(...)):
    try:
        rows = update_student_gpa(student_id, gpa)
        if rows:
            console.print(f"[green]Updated student ID {student_id} successfully.[/green]")
        else:
            console.print(f"[yellow]No student found with ID {student_id}[/yellow]")
    except Exception as e:
        console.print(f"[red]Failed to update GPA: {e}[/red]")


@app.command()
def delete(student_id: int = typer.Option(...)):
    try:
        rows = delete_student(student_id)
        console.print(f"[green]{rows} student(s) deleted.[/green]")
    except Exception as e:
        console.print(f"[red]Failed to delete student: {e}[/red]")


if __name__ == "__main__":
    check_venv()
    init_db()
    app()

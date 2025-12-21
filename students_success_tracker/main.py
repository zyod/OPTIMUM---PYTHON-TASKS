import sys

if sys.prefix == sys.base_prefix:
    raise RuntimeError(
        "Virtual environment not active. "
        "Activate it with: source .venv/bin/activate"
    )


from db import init_db

def main():
    init_db()
    print("success_tracker CLI started. Database is ready.")


if __name__ == "__main__":
    main()

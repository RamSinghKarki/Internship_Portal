"""Application entry point.

Runs the Flask development server:
    python app.py            # http://127.0.0.1:5000

Database setup and demo data live in seed.py:
    python seed.py

For production, point a WSGI server at the factory instead, e.g.:
    gunicorn "app:create_app()"
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

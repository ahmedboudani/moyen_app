from setuptools import setup, find_packages

setup(
    name="moyyen",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Flask==2.0.1",
        "Flask-SQLAlchemy==2.5.1",
        "reportlab==3.6.0",
        "arabic_reshaper==2.1.3",
        "python-bidi==0.4.2",
        "waitress==2.1.2",
        "psycopg2-binary==2.9.1",
        "pandas==1.3.3",
        "openpyxl==3.0.9",
        "Flask-Login==0.5.0",
        "Werkzeug==2.0.1",
        "email-validator==1.1.3",
        "gunicorn==20.1.0",
    ],
)

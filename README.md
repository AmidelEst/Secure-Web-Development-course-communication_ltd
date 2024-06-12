
# Communication_LTD Project

## Overview

This is a Django-based project for managing customer communications. The project includes features like user registration, password management, and profile management.

## Prerequisites

- MySQL Community Server
- MySQL Workbench
- Python 3.12 or later

## Installation

Follow these steps to set up the project in your local environment:

### 1. Clone the Repository

```sh
git clone <url>
```

### 2. Set Up Virtual Environment

Create a virtual environment and activate it:

```sh
python -m venv .venv
.venv\Scripts\activate
cd <project-directory>
```

### 3. Install Dependencies

Navigate to the project directory and install the required dependencies:

```sh
cd communication_ltd
pip install -r requirements.txt
```

### 4. Configure the Database

1. Open MySQL Workbench and create a new database for the project and name it: `communication_ltd_db3`.

2. Update the database configuration in `communication_ltd/settings.py` with your database details:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'communication_ltd_db3',
        'USER': 'your_database_user',
        'PASSWORD': 'your_database_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 5. Apply Migrations

Run the following commands to apply the migrations and set up the database schema:

```sh
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser

Create a superuser to access the Django admin interface:

```sh
python manage.py createsuperuser
```

### 7. Collect Static Files

Collect all static files:

```sh
python manage.py collectstatic
```

### 8. Run the Server

Start the Django development server:

```sh
python manage.py runserver
```

### 9. Deactivate the Virtual Environment

When you're done working on the project, deactivate the virtual environment:

```sh
deactivate
```

## Additional Information

- Access the admin interface at `http://127.0.0.1:8000/admin/` with the superuser credentials.
- The application home page is accessible at `http://127.0.0.1:8000/`.

## Contact

For any questions or support, please contact andamitpom14@gmail.com.

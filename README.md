# Credit Approval System - Backend

This is a Django backend project for a credit approval system, created as part of an internship assignment. The application is fully containerized using Docker.

## How to Run

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/CoderNikkcoder/django-credit-api.git
    ```

2.  **Navigate into the project directory:**
    ```bash
    cd django-credit-api
    ```

3.  **Build and run the Docker containers:**
    ```bash
    docker-compose up --build
    ```

4.  **In a new terminal, run database migrations and import data:**
    ```bash
    docker-compose exec web python manage.py migrate
    docker-compose exec web python manage.py import_data
    ```

The application will be running at `http://127.0.0.1:8000/`.

## API Endpoints

-   `POST /api/register/`
-   `POST /api/check-eligibility/`
-   `POST /api/create-loan/`
-   `GET /api/view-loan/<loan_id>/`
-   `GET /api/view-loans/<customer_id>/`


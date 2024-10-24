# Fintech Project: Banking Backend Simulation

## Description

This project simulates the interaction between a user and a banking application. It consists of multiple microservices working together to handle credit applications, scoring, and loan management. 

**Tech Stack:** Python; Docker Compose, CI/CD, REST API, PostgreSQL, Clickhouse, Kafka, Jobs Scheduler

Below are the descriptions of the main services:
- *Product Engine*: managing and storing banking products, client data, loan agreements and payment schedules

- *Origination*: handling credit applications
    - Receives applications, validates terms via Product Engine, and sends them to Scoring for evaluation.
     - Updates application statuses (Created, Pending, Approved, Rejected).
     - Manages application cancellation with reprocessing pending requests if needed.

- *Scoring*: processing application scoring (Approve/Reject).

- *Gateway*: the client-facing API that routes requests to the appropriate services (e.g., product list from Product Engine, create applications in Origination).

## Flow

![flow](https://github.com/user-attachments/assets/1c0d67ef-b02f-4f10-b07f-6836223c1153)


## Instructions:

The details are available in
- To run all the databases + migrations + services:
    ```bash
    docker-compose up --build -d
    ```

- Swagger UI is available at (locally):
    - Product engine: http://0.0.0.0:80/docs#/
    - Origination: http://0.0.0.0:90/docs#/
    - Gateway: http://0.0.0.0:7022/docs#/
    - Scoring: http://0.0.0.0:8008/docs#/

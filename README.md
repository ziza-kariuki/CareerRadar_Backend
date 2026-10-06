# CareerRadar Backend

> Flask REST API and PostgreSQL database for [CareerRadar](https://github.com/ziza-kariuki/Group4Project_CareerRadar), a job discovery platform.

## Table of Contents

- [Overview](#overview)
- [Status](#status)
- [Core Features](#core-features)
- [Tech Stack](#tech-stack)
- [API Endpoints](#api-endpoints)
- [Database Tables](#database-tables)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Data Source](#data-source)

## Overview

CareerRadar's Phase 1 was a React job explorer that called the Jobicy API directly. This repository holds the Phase 2 backend: a Flask API that lets the frontend search jobs, register and log in users, and save jobs that persist between visits.

## Core Features

- **User authentication:** sign up, log in, log out, and session check, with hashed passwords
- **Job search:** search and filter jobs through our own API, backed by Jobicy
- **Saved jobs:** logged-in users can save, list, and remove jobs
- **Validation and errors:** invalid requests are rejected and errors return consistent JSON

## Tech Stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| Language and framework | Python and Flask | REST API |
| Database | PostgreSQL | Stores users, jobs, and saved jobs |
| ORM | SQLAlchemy | Maps Python classes to tables |
| Migrations | Flask-Migrate | Tracks schema changes |
| Serialization | Marshmallow | Validates input and formats output |
| Security | Flask-Bcrypt | Hashes passwords |
| Cross-origin access | Flask-CORS | Lets the React app call the API |

## API Endpoints

| Method | Route | Login required | Purpose |
| --- | --- | --- | --- |
| `POST` | `/signup` | No | Create an account |
| `POST` | `/login` | No | Start a session |
| `DELETE` | `/logout` | Yes | End the session |
| `GET` | `/check_session` | No | Return the current user, or `401` |
| `GET` | `/jobs` | No | Search and filter jobs |
| `GET` | `/jobs/<id>` | No | Get one job in full |
| `GET` | `/saved-jobs` | Yes | List the user's saved jobs |
| `POST` | `/saved-jobs` | Yes | Save a job |
| `DELETE` | `/saved-jobs/<id>` | Yes | Remove a saved job |

Errors are returned in a consistent format:

```json
{ "error": "Job not found" }
```

## Database Tables

| Table | Purpose |
| --- | --- |
| `users` | User account details |
| `jobs` | Job listings |
| `saved_jobs` | Links users to the jobs they save |

A user can save many jobs, and a job can be saved by many users, so `saved_jobs` connects the two.

## Project Structure

```text
backend/
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models/
│   │   ├── user.py
│   │   ├── job.py
│   │   └── saved_job.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── jobs.py
│   │   └── saved_jobs.py
│   ├── services/
│   │   └── jobicy_service.py
│   ├── schemas/
│   └── utils/
├── migrations/
├── tests/
├── config.py
├── requirements.txt
├── run.py
└── .env          (not committed)
```

| Folder or file | Purpose |
| --- | --- |
| `app/__init__.py` | Creates and configures the Flask app |
| `app/extensions.py` | Shared tools such as the database and migration objects |
| `app/models/` | Database models |
| `app/routes/` | API endpoints, grouped by feature |
| `app/services/` | Logic that talks to external services, such as Jobicy |
| `app/schemas/` | Marshmallow validation and serialization |
| `app/utils/` | Small helper functions |
| `migrations/` | Database migration files |
| `tests/` | Tests |
| `config.py` | App and database configuration |
| `run.py` | Starts the development server |

## Getting Started

> Update these commands once the setup is finalised.

```bash
# Clone the repository
git clone https://github.com/<your-username>/<backend-repo>.git
cd <backend-repo>

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create the .env file (see below), then apply the migrations
flask --app run db upgrade

# Start the server
python run.py
```

## Environment Variables

Create a `.env` file in the project root. It holds secrets, so it must never be committed.

```text
SECRET_KEY=<your-secret-key>
DATABASE_URI=postgresql://<user>:<password>@localhost:5432/<database-name>
```

## Data Source

Job listings come from the [Jobicy Remote Jobs API](https://jobicy.com/jobs-rss-feed). The backend requests up to 20 jobs per search.

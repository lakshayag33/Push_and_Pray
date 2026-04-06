# 🫀 VitalSync — Context-Aware Daily Health Decision Assistant

> An AI-powered personal wellness platform that tracks daily habits, computes a health score across 10 parameters, and delivers context-aware suggestions using Google Gemini — all through a sleek, dark-themed web interface.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Running the App](#running-the-app)
- [Architecture](#architecture)
  - [Role-Based Access Control](#role-based-access-control)
  - [Health Score Engine](#health-score-engine)
  - [AI Engine (Gemini)](#ai-engine-gemini)
  - [Background Scheduler](#background-scheduler)
- [API Endpoints](#api-endpoints)
- [Database Models](#database-models)
- [Default Credentials](#default-credentials)
- [Screenshots](#screenshots)
- [License](#license)

---

## Overview

**VitalSync** is a Flask web application where users take a daily health quiz covering sleep, nutrition, activity, stress, and mood. The app computes a weighted health score (0–100), sends the data to Google Gemini AI for a personalized wellness suggestion, and stores everything for longitudinal trend analysis. Users can optionally share their progress with approved health reviewers.

---

## Features

| Feature | Description |
|---|---|
| **Daily Health Quiz** | 15-field form covering sleep, steps, calories, water, stress, mood, screen time, exercise, outdoor time, meal timings, and more |
| **Health Score (0–100)** | Rule-based scorer with weighted parameters (sleep 20%, stress 15%, steps 15%, water 10%, screen 10%, meals 10%, calories 10%, mood 5%, exercise 3%, outdoor 2%) |
| **AI-Powered Suggestions** | Google Gemini analyzes quiz data + 7-day history to provide a single, prioritized suggestion with urgency detection |
| **AI Chat Assistant** | Conversational chatbot that knows the user's logged health data and answers wellness questions |
| **7-Day Trend Charts** | Interactive Chart.js line charts for 9 health metrics (sleep, steps, mood, stress, water, calories, screen time, exercise, outdoor) |
| **Health Log History** | Paginated history view with scores, statuses, and suggestions for every past entry |
| **Reviewer System** | Users can invite approved reviewers to view their trend charts — with accept/decline/revoke controls |
| **Admin Panel** | Admin manages all users and approves/rejects reviewer registrations |
| **Email Reminders** | APScheduler sends daily 8 AM reminder emails to users who haven't taken the quiz |
| **Auto-Analyze** | Background job at 11:59 PM generates suggestions for any quiz submissions missing one |
| **Urgency Detection** | Both quiz analysis and chat detect critical health patterns and flag urgent warnings |
| **Dark Themed UI** | Glassmorphism design with Bootstrap 5, Inter font, custom CSS, and smooth animations |
| **CSRF Protection** | WTForms CSRF on all form-based routes; API blueprint exempted for JSON endpoints |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3, Flask 3.1 |
| **Database** | SQLite (via Flask-SQLAlchemy) |
| **Authentication** | Flask-Login with Werkzeug password hashing |
| **AI / LLM** | Google Gemini (via `google-generativeai` SDK) |
| **Scheduling** | APScheduler (BackgroundScheduler) |
| **Email** | Flask-Mail (SMTP) |
| **Forms / CSRF** | Flask-WTF, WTForms |
| **Frontend** | Bootstrap 5.3, Bootstrap Icons, Chart.js, Jinja2 templates |
| **Typography** | Google Fonts (Inter) |

---

## Project Structure

```
Push_and_Pray/
├── run.py                          # Application entry point
├── requirements.txt                # Python dependencies
├── instance/
│   └── health.db                   # SQLite database (auto-created)
└── app/
    ├── __init__.py                 # Flask app factory, extension init, admin seeding
    ├── config.py                   # Configuration (env vars, secrets, mail, Gemini)
    ├── models.py                   # SQLAlchemy models (User, HealthLog, Suggestion, ReviewerInvite)
    │
    ├── blueprints/
    │   ├── __init__.py
    │   ├── auth.py                 # Login, register, logout, role-based redirect
    │   ├── user.py                 # Dashboard, quiz, history, chatbot, reviewer invites
    │   ├── reviewer.py             # Reviewer dashboard, accept/decline invites, view user charts
    │   ├── admin.py                # Admin panel, approve/reject reviewers
    │   └── api.py                  # REST API — chart data (/api/charts/<metric>), chat (/api/chat)
    │
    ├── services/
    │   ├── __init__.py
    │   ├── score_engine.py         # Rule-based health score calculator (0–100)
    │   ├── gemini_engine.py        # Gemini AI integration (quiz analysis + chat modes)
    │   └── scheduler.py            # APScheduler jobs (daily reminder + auto-analyze)
    │
    ├── templates/
    │   ├── base.html               # Base layout (navbar, flash messages, footer)
    │   ├── main/
    │   │   └── index.html          # Landing page (hero, features, CTA)
    │   ├── auth/
    │   │   ├── login.html          # Login form
    │   │   └── register.html       # Registration form (user or reviewer role)
    │   ├── user/
    │   │   ├── dashboard.html      # User dashboard (score, suggestion, charts, invites)
    │   │   ├── quiz.html           # Daily health quiz form (15 fields)
    │   │   ├── history.html        # Paginated health log history
    │   │   └── chatbot.html        # AI chat assistant interface
    │   ├── reviewer/
    │   │   ├── dashboard.html      # Reviewer panel (pending + accepted invites)
    │   │   └── charts.html         # View a user's trend charts
    │   └── admin/
    │       └── panel.html          # Admin panel (user list, reviewer approvals)
    │
    └── static/
        ├── css/
        │   └── custom.css          # Custom styles (glassmorphism, dark theme, animations)
        └── js/
            ├── charts.js           # Chart.js initialization and API fetching
            └── chatbot.js          # Chat UI logic (conversation state, API calls, bubbles)
```

---

## Getting Started

### Prerequisites

- **Python 3.9+**
- **pip** (Python package manager)
- A **Google Gemini API key** (optional — the app has fallback suggestions if no key is set)

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd Push_and_Pray

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the `Push_and_Pray/` root directory:

```env
# Required
SECRET_KEY=your-secret-key-here

# Google Gemini AI (optional — fallback works without it)
GEMINI_API_KEY=your-gemini-api-key

# Database (optional — defaults to SQLite)
DATABASE_URL=sqlite:///health.db

# Email / SMTP (optional — needed for daily reminders)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

> **Note:** If `GEMINI_API_KEY` is not set, the app uses built-in fallback suggestions based on the computed score. The chat assistant will return a polite error message.

### Running the App

```bash
python run.py
```

The app starts on **http://localhost:5000** in debug mode.

---

## Architecture

### Role-Based Access Control

The app supports three user roles with distinct dashboards:

| Role | Access | Notes |
|---|---|---|
| **User** | Dashboard, Quiz, History, Chatbot, Invite Reviewers | Default role on registration |
| **Reviewer** | Reviewer Dashboard, View User Charts | Must be approved by admin before activation |
| **Admin** | Admin Panel (user management, reviewer approvals) | Seeded on first run with `admin@health.app` |

Role-based redirects are enforced on login and across all blueprint routes.

### Health Score Engine

The score is computed across **10 weighted parameters** totaling 100 points:

| Parameter | Max Points | Best Value |
|---|---|---|
| Sleep Hours | 20 | ≥ 8 hours |
| Stress Level | 15 | ≤ 2 (low) |
| Steps | 15 | ≥ 10,000 |
| Water Intake | 10 | ≥ 2,500 ml |
| Screen Time | 10 | ≤ 2 hours |
| Meal Timing | 10 | 3 meals in ideal windows |
| Calories | 10 | 1,800–2,500 kcal |
| Mood | 5 | ≥ 8 (high) |
| Exercise | 3 | ≥ 45 minutes |
| Outdoor Time | 2 | ≥ 60 minutes |

### AI Engine (Gemini)

The Gemini integration operates in two modes via a shared system prompt:

**Mode 1 — Post-Quiz Analysis:**
- Receives today's metrics, computed score, and 7-day history
- Returns a single prioritized suggestion following a defined priority order (Sleep → Stress → Meals → Hydration → ...)
- Detects urgency conditions (e.g., sleep < 4h for 2/3 days, stress ≥ 9 for 2/3 days)
- Classifies status as `excellent`, `good`, or `needs_improvement`

**Mode 2 — Chat Assistant:**
- Contextual conversation using the user's logged health data
- Scope-restricted to health and wellness topics only
- Detects urgency in user messages (e.g., mentions of chest pain, self-harm language)
- Maintains conversation history in browser memory

### Background Scheduler

Two APScheduler cron jobs run automatically:

| Job | Schedule | Purpose |
|---|---|---|
| `daily_reminder` | 8:00 AM daily | Sends email reminders to users who haven't taken the quiz |
| `auto_analyze` | 11:59 PM daily | Generates AI suggestions for any quiz entries missing one |

---

## API Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/charts/<metric>` | Returns 7-day chart data for a metric (sleep, steps, mood, stress, water, calories, screen, exercise, outdoor) | Login required |
| `GET` | `/api/charts/<metric>?user_id=<id>` | Returns chart data for another user (reviewer access required) | Reviewer |
| `POST` | `/api/chat` | Sends a message to the AI chat assistant. Body: `{ message, conversation }` | Login required |

> The API blueprint is exempted from CSRF protection since it uses JSON payloads.

---

## Database Models

| Model | Purpose | Key Fields |
|---|---|---|
| **User** | Authentication & roles | `email`, `password_hash`, `role` (user/reviewer/admin), `reviewer_status` |
| **HealthLog** | Daily health quiz data | 15 health metrics + `user_id`, `date` |
| **Suggestion** | AI-generated suggestions | `score`, `suggestion_text`, `status`, `urgent`, linked to `HealthLog` |
| **ReviewerInvite** | User ↔ Reviewer relationships | `user_id`, `reviewer_id`, `status` (pending/accepted/revoked) |

---

## Default Credentials

On first run, the app seeds a default admin account:

| Field | Value |
|---|---|
| Email | `admin@health.app` |
| Password | `admin123` |

> ⚠️ **Change these immediately in production.**

---

## Screenshots

*Coming soon — run the app locally to explore the full UI.*

---

## License

This project is part of the **inCSEption26** hackathon submission.


# Automated Event Planner and Approval System - Phase 4

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.x-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-latest-blue.svg)
![Git](https://img.shields.io/badge/Git-latest-orange.svg)
![AI-Assisted](https://img.shields.io/badge/AI--Assisted-Enabled-blueviolet.svg)

## Executive Summary
The primary goal of this project is to digitize institutional workflows at JNU Jaipur, replacing paper-based approvals with a transparent digital system. This platform streamlines event planning and ensures accountability at every layer of the institution.

## Phase 4 Scope
This repository encompasses the "Approval Workflow Automation" phase. It implements a multi-level approval state machine transitioning events from `Draft` -> `Pending Faculty` -> `Pending Dept Head` -> `Approved` or `Rejected`. Key features include role-based decision interfaces, comprehensive approval history tracking, and conditional UI rendering. The database has been extended to include the new `Approvals` entity and updated `Events` status fields.

## Tech Stack
- **Backend:** Python 3.8+, Flask 2.x, Jinja2, SQLAlchemy, Gunicorn
- **Frontend:** HTML5, CSS3, JavaScript
- **Database:** PostgreSQL

## Installation Guide
1. Clone the repository:
   ```bash
   git clone https://github.com/CyberSential22/epas-phase-5.git
   cd epas-phase-5
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables locally in a `.env` file.
5. Run the application:
   ```bash
   flask run
   ```

## Project Structure
```text
epas-phase-5/
├── app/               # Main application package
│   ├── blueprints/    # Flask blueprints
│   ├── models/        # Database models
│   ├── utils/         # Utility scripts including ip_utils.py
│   ├── __init__.py    # App factory
│   └── config.py      # App configurations
├── instance/          # Local configurations (do not commit)
├── static/            # Static assets
├── templates/         # Jinja2 templates
├── requirements.txt   # Python dependencies
├── run.py             # App entry point
└── vercel.json        # Vercel proxy configuration
```

## Deployment Overview
- **Vercel**: Frontend Proxy
- **Render**: Backend Host
- **Supabase**: PostgreSQL Database

## Acknowledgments
- **Project Team:** Kashif Shaikh, Aditya Gond, Yaduvansh Singh Ranawat (JNU Jaipur)
- **Project Guide:** Ms. Saumya
- *Ethical Use Note: Adheres to Section 6.5 regarding the ethical use of AI-assisted tools for research and debugging while maintaining student ownership of core design.*

## License
[MIT License](LICENSE)

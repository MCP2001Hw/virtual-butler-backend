# Virtual Butler — Smart Home Backend

Group coursework for F29SO Software Engineering — Heriot-Watt University.
7-person team. **My contribution: the entire Python/Flask backend and MySQL database schema.**

A REST API backend for a 2030 smart home management application. Handles user authentication, device management, room/house configuration, energy statistics, billing, and weather data — all with background auto-update workers.

---

## My Contribution

Solely responsible for the backend across all modules:

| File | Description |
|---|---|
| `app.py` | Flask app — 18 REST endpoints, session management, routing |
| `database_execute.py` | MySQL connection and query execution layer |
| `user_management.py` | User CRUD, role management (owner/admin/user) |
| `device_management.py` | Device registration, status, scheduling |
| `room_management.py` | Room and house profile management |
| `house_management.py` | House-level data and ownership |
| `permissions_management.py` | Access control — grant/revoke per-user device permissions |
| `device_stats_auto_update.py` | Background worker — polls and updates device statistics |
| `device_stats_update_database.py` | Device stats database write logic |
| `bill_stats_auto_update.py` | Background worker — recalculates energy bills |
| `bill_stats_update_database.py` | Billing database write logic |
| `weather_auto_update.py` | Background worker — fetches weather data on a schedule |
| `weather_update_database.py` | Weather database write logic |
| `weather_API.py` | Weather API integration |
| `auto_update.py` | Coordinates all background workers |

---

## API Overview

| Category | Endpoints |
|---|---|
| Auth | Login, register, logout |
| Users | Get/update profile, role management |
| Devices | Add, remove, toggle, schedule |
| Rooms & Houses | Create rooms, assign devices, manage house profile |
| Permissions | Grant/revoke/edit user access per device or room |
| Stats & Billing | Energy consumption, cost breakdown, historical comparison |
| Weather | Current conditions, forecast display |

---

## Setup

1. Create a MySQL database and load the schema
2. Set your database credentials as environment variables:

```bash
export DB_HOST=your_host
export DB_PORT=your_port
export DB_USER=your_user
export DB_PASSWORD=your_password
export DB_NAME=your_database
```

3. Install dependencies and run:

```bash
pip install flask flask-session mysql-connector-python bcrypt requests
python app.py
```

---

## Notes

- Frontend (React.js) was built by other team members and is not included here
- `flask_session/` is excluded from this repo — add it to `.gitignore`
- This was my first backend project; a more refined version was later built for my dissertation using PostgreSQL/PostGIS and deployed on Render

---

## Related

- [Location-Based Diary](https://github.com/MCP2001Hw/location-based-diary) — dissertation project, built on lessons learned here

# WordPress Database ADK Agent

This project uses Google ADK to chat with a WordPress MySQL database through a safe, read-only tool.

## What it does

- Runs an ADK chat agent
- Lets the agent query a WordPress database
- Blocks write operations like `INSERT`, `UPDATE`, `DELETE`, `DROP`, and `ALTER`
- Works with a direct remote MySQL connection or an SSH tunnel

## Project layout

```text
wordpress_db_agent/
  __init__.py
  agent.py
.env
.env.example
README.md
requirements.txt
```

## Install

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configure

Copy `.env.example` to `.env` and fill in your values.

For an SSH tunnel, set:

- `WP_DB_HOST=127.0.0.1`
- `WP_DB_PORT=3307`

For a direct remote database connection, set:

- `WP_DB_HOST=your-db-server-host`
- `WP_DB_PORT=3306`

## Run the agent

From this folder:

```bash
adk web
```

Then open the browser UI, select `wordpress_db_agent`, and ask questions like:

- `Show the 10 latest posts`
- `How many users are in wp_users?`
- `List published posts with their titles`

## Windows SSH tunnel

If the database server only allows SSH access, start a tunnel in PowerShell:

```powershell
ssh -N -L 3307:127.0.0.1:3306 your_ssh_user@your_server
```

Keep that window open while you use the agent or a MySQL client.

## Notes

- Use a dedicated MySQL account with `SELECT` only.
- Prefer an SSH tunnel over exposing port `3306` publicly.
- WordPress databases can be large, so keep queries narrow and use `LIMIT` where possible.


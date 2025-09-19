import psycopg2

# Connect with your Supabase Postgres URI
conn = psycopg2.connect(
    "postgresql://postgres:qOe8OeQoGqOhQJia@db.wfnhabdtwcjebmyeglnt.supabase.co:5432/postgres",
    sslmode="require"
)
cur = conn.cursor()

def get_lock_kiosk_status() -> dict:

    # Fetch all rows (assuming table has columns: key, value)
    cur.execute("SELECT key, value FROM lock_kiosk_status WHERE deleted_at is NULL;")
    rows = cur.fetchall()

    # Convert to dictionary
    lock_status = {key: value for key, value in rows}

    cur.close()
    conn.close()
    return lock_status
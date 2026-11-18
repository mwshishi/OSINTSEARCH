import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="osintSearchDB",
    user="postgres",
    password="admin",
    port="5432"
)
cur = conn.cursor()

def ensure_columns(table_name, expected_columns):
    for column_name, column_def in expected_columns.items():
        cur.execute(f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s;
        """, (table_name, column_name))
        if not cur.fetchone():
            print(f"[INFO] Adding column {column_name} to {table_name}")
            cur.execute(f'ALTER TABLE {table_name} ADD COLUMN "{column_name}" {column_def};')

expected_username_info_columns = {
    "username": "VARCHAR(50) UNIQUE DEFAULT 'N/A'",
    "amazon_status": "VARCHAR(20) DEFAULT 'N/A'",
    "instagram_status": "VARCHAR(20) DEFAULT 'N/A'",
    "quora_status": "VARCHAR(20) DEFAULT 'N/A'",
    "spotify_status": "VARCHAR(20) DEFAULT 'N/A'",
    # ➕ Add more columns here as needed
    "7cups_status": "VARCHAR(20) DEFAULT 'N/A'",
    "twitter_status": "VARCHAR(20) DEFAULT 'N/A'",
    "tryhackme_status": "VARCHAR(20) DEFAULT 'N/A'"
}

expected_phone_info_columns = {
    "phone": "VARCHAR(20) UNIQUE DEFAULT 'N/A'",
    "location": "TEXT DEFAULT 'N/A'",
    "region_code": "VARCHAR(10) DEFAULT 'N/A'",
    "timezone": "TEXT DEFAULT 'N/A'",
    "operator": "VARCHAR(50) DEFAULT 'N/A'",
    "valid": "BOOLEAN DEFAULT FALSE",
    "possible": "BOOLEAN DEFAULT FALSE",
    "formatted_international": "VARCHAR(30) DEFAULT 'N/A'",
    "formatted_mobile": "VARCHAR(30) DEFAULT 'N/A'",
    "original_number": "BIGINT DEFAULT NULL",
    "e164": "VARCHAR(20) DEFAULT 'N/A'",
    "country_code": "INTEGER DEFAULT NULL",
    "local_number": "BIGINT DEFAULT NULL",
    # ➕ Add more columns here as needed
    "type": "VARCHAR(30) DEFAULT 'N/A'"  # Uncomment if you want to track phone type
}


expected_email_info_columns = {
    "email": "VARCHAR(100) UNIQUE DEFAULT 'N/A'",
    "amazon_status": "VARCHAR(20) DEFAULT 'N/A'",
    "instagram_status": "VARCHAR(20) DEFAULT 'N/A'",
    "quora_status": "VARCHAR(20) DEFAULT 'N/A'",
    "spotify_status": "VARCHAR(20) DEFAULT 'N/A'",
    # ➕ Add more columns here as needed
    "7cups_status": "VARCHAR(20) DEFAULT 'N/A'",
    "wordpress_status": "VARCHAR(20) DEFAULT 'N/A'"
}

try:
    # 1. Create tables with updated naming
    cur.execute("""
        CREATE TABLE IF NOT EXISTS email_info (
            email_id SERIAL PRIMARY KEY,
            email VARCHAR(100) UNIQUE DEFAULT 'N/A',
            amazon_status VARCHAR(20) DEFAULT 'N/A',
            instagram_status VARCHAR(20) DEFAULT 'N/A',
            quora_status VARCHAR(20) DEFAULT 'N/A',
            spotify_status VARCHAR(20) DEFAULT 'N/A',
            twitter_status VARCHAR(20) DEFAULT 'N/A'
        );
    """)
    ensure_columns("email_info", expected_email_info_columns)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS username_info (
            username_id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE DEFAULT 'N/A',
            amazon_status VARCHAR(20) DEFAULT 'N/A',
            instagram_status VARCHAR(20) DEFAULT 'N/A',
            quora_status VARCHAR(20) DEFAULT 'N/A',
            spotify_status VARCHAR(20) DEFAULT 'N/A'
        );
    """)
    ensure_columns("username_info", expected_username_info_columns)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS phone_info (
        phone_id SERIAL PRIMARY KEY,
        phone VARCHAR(20) UNIQUE DEFAULT 'N/A',
        location TEXT DEFAULT 'N/A',
        region_code VARCHAR(10) DEFAULT 'N/A',
        timezone TEXT DEFAULT 'N/A',
        operator VARCHAR(50) DEFAULT 'N/A',
        valid BOOLEAN DEFAULT FALSE,
        possible BOOLEAN DEFAULT FALSE,
        formatted_international VARCHAR(30) DEFAULT 'N/A',
        formatted_mobile VARCHAR(30) DEFAULT 'N/A',
        original_number BIGINT DEFAULT NULL,
        e164 VARCHAR(20) DEFAULT 'N/A',
        country_code INTEGER DEFAULT NULL,
        local_number BIGINT DEFAULT NULL
    );
""")
    ensure_columns("phone_info", expected_phone_info_columns)


    conn.commit()


except Exception as e:
    print("Error:", e)

cur.close()
conn.close()

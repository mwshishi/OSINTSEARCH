import psycopg2

def update_email_info(email, site_statuses):
    conn = psycopg2.connect(
        host="localhost",
        database="osintSearchDB",
        user="postgres",
        password="admin",
        port="5432"
    )
    cur = conn.cursor()

    # Ensure the email exists in table
    cur.execute("""
        INSERT INTO email_info (email)
        VALUES (%s)
        ON CONFLICT (email) DO NOTHING;
    """, (email,))

    # Update each site status, keeping "Found" permanent
    for site, is_found in site_statuses.items():
        column = f"{site.lower()}_status"
        new_value = "Found" if is_found else "Not Found"

        # Only update if previous is "N/A" or "Not Found" and new is "Found"
        cur.execute(f"""
            UPDATE email_info
            SET "{column}" = CASE
                WHEN "{column}" = 'N/A' AND %s = 'Not Found' THEN 'Not Found'
                WHEN "{column}" != 'Found' AND %s = 'Found' THEN 'Found'
                ELSE "{column}"
            END
            WHERE email = %s;
        """, (new_value, new_value, email))

    conn.commit()
    cur.close()
    conn.close()

def update_username_info(username, site_statuses):
    conn = psycopg2.connect(
        host="localhost",
        database="osintSearchDB",
        user="postgres",
        password="admin",
        port="5432"
    )
    cur = conn.cursor()

    # Ensure the username exists in the table
    cur.execute("""
        INSERT INTO username_info (username)
        VALUES (%s)
        ON CONFLICT (username) DO NOTHING;
    """, (username,))

    for site, is_found in site_statuses.items():
        column = f"{site.lower()}_status"
        new_value = "Found" if is_found else "Not Found"

        cur.execute(f"""
            UPDATE username_info
            SET "{column}" = CASE
                WHEN "{column}" = 'N/A' AND %s = 'Not Found' THEN 'Not Found'
                WHEN "{column}" != 'Found' AND %s = 'Found' THEN 'Found'
                ELSE "{column}"
            END
            WHERE username = %s;
        """, (new_value, new_value, username))

    conn.commit()
    cur.close()
    conn.close()

def update_phone_info(phone, info_dict):
    try:
        conn = psycopg2.connect(
            host="localhost", database="osintSearchDB",
            user="postgres", password="admin", port="5432"
        )
        cur = conn.cursor()

        cur.execute("SELECT phone FROM phone_info WHERE phone = %s;", (phone,))
        exists = cur.fetchone()

        if exists:
            assignments = ', '.join([f'"{k}" = %s' for k in info_dict])
            values = list(info_dict.values()) + [phone]
            cur.execute(f"UPDATE phone_info SET {assignments} WHERE phone = %s;", values)
        else:
            columns = ', '.join(['phone'] + [f'"{k}"' for k in info_dict])
            placeholders = ', '.join(['%s'] * (1 + len(info_dict)))
            values = [phone] + list(info_dict.values())
            cur.execute(f"INSERT INTO phone_info ({columns}) VALUES ({placeholders});", values)

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"[DB ERROR] update_phone_info failed: {e}")
        raise

def fetch_phone_info(phone):
    try:
        conn = psycopg2.connect(host="localhost", database="osintSearchDB", user="postgres", password="admin", port="5432")
        cur = conn.cursor()
        cur.execute("SELECT * FROM phone_info WHERE phone = %s;", (phone,))
        row = cur.fetchone()
        if row:
            colnames = [desc[0] for desc in cur.description]
            return dict(zip(colnames, row))
        return None
    except Exception as e:
        print(f"[DB ERROR] fetch_phone_info failed: {e}")
        return None
    finally:
        if cur: cur.close()
        if conn: conn.close()

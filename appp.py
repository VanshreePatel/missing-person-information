import streamlit as st
import sqlite3
import pandas as pd

# --- User database setup ---
def init_user_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    result = c.fetchone()
    conn.close()
    return result

# --- Missing person database setup ---
def init_person_db():
    conn = sqlite3.connect("missing_persons.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS person (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            last_seen TEXT,
            contact TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_person(name, age, gender, last_seen, contact):
    conn = sqlite3.connect("missing_persons.db")
    c = conn.cursor()
    c.execute("INSERT INTO person (name, age, gender, last_seen, contact, status) VALUES (?, ?, ?, ?, ?, ?)",
              (name, age, gender, last_seen, contact, "Missing"))
    conn.commit()
    conn.close()

def get_all_persons():
    conn = sqlite3.connect("missing_persons.db")
    df = pd.read_sql_query("SELECT * FROM person", conn)
    conn.close()
    return df

def mark_found(person_id):
    conn = sqlite3.connect("missing_persons.db")
    c = conn.cursor()
    c.execute("UPDATE person SET status='Found' WHERE id=?", (person_id,))
    conn.commit()
    conn.close()

def delete_person(person_id):
    conn = sqlite3.connect("missing_persons.db")
    c = conn.cursor()
    c.execute("DELETE FROM person WHERE id=?", (person_id,))
    conn.commit()
    conn.close()

# --- Registration page ---
def registration_page():
    st.title("📝 Register")

    username = st.text_input("Create Username")
    password = st.text_input("Create Password", type="password")

    if st.button("Register"):
        if username and password:
            success = register_user(username, password)
            if success:
                st.success("Registration successful. You can now log in.")
            else:
                st.error("Username already exists.")
        else:
            st.warning("Please fill all fields.")

# --- Login page ---
def login_page():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if verify_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username}!")
        else:
            st.error("Invalid credentials.")

# --- Main app after login ---
def main_app():
    st.title("🕵️ Missing Person Information System")

    menu = ["Add Person", "View All", "Mark Found", "Delete", "Logout"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Add Person":
        st.subheader("➕ Add Missing Person")
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0, max_value=120)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        last_seen = st.text_input("Last Seen Location")
        contact = st.text_input("Contact Info")

        if st.button("Add"):
            if name and last_seen and contact:
                add_person(name, age, gender, last_seen, contact)
                st.success(f"{name} added.")
            else:
                st.warning("Fill all required fields.")

    elif choice == "View All":
        st.subheader("📋 All Records")
        df = get_all_persons()
        st.dataframe(df)

    elif choice == "Mark Found":
        st.subheader("✅ Mark Person as Found")
        df = get_all_persons()
        if not df.empty:
            person_id = st.selectbox("Select ID", df["id"])
            if st.button("Mark Found"):
                mark_found(person_id)
                st.success("Status updated to Found.")

    elif choice == "Delete":
        st.subheader("🗑️ Delete Record")
        df = get_all_persons()
        if not df.empty:
            person_id = st.selectbox("Select ID to Delete", df["id"])
            if st.button("Delete"):
                delete_person(person_id)
                st.warning("Deleted.")

    elif choice == "Logout":
        st.session_state.logged_in = False
        st.success("Logged out.")

# --- Main controller ---
def main():
    init_user_db()
    init_person_db()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        page = st.sidebar.radio("Choose Page", ["Login", "Register"])
        if page == "Login":
            login_page()
        else:
            registration_page()
    else:
        main_app()

if __name__ == "__main__":
    main()

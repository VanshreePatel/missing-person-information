import streamlit as st
import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect('missing_persons.db')
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
    conn = sqlite3.connect('missing_persons.db')
    c = conn.cursor()
    c.execute("INSERT INTO person (name, age, gender, last_seen, contact, status) VALUES (?, ?, ?, ?, ?, ?)",
              (name, age, gender, last_seen, contact, 'Missing'))
    conn.commit()
    conn.close()

def get_all_persons():
    conn = sqlite3.connect('missing_persons.db')
    df = pd.read_sql_query("SELECT * FROM person", conn)
    conn.close()
    return df

def mark_found(person_id):
    conn = sqlite3.connect('missing_persons.db')
    c = conn.cursor()
    c.execute("UPDATE person SET status='Found' WHERE id=?", (person_id,))
    conn.commit()
    conn.close()

def delete_person(person_id):
    conn = sqlite3.connect('missing_persons.db')
    c = conn.cursor()
    c.execute("DELETE FROM person WHERE id=?", (person_id,))
    conn.commit()
    conn.close()

def main():
    st.title("🕵️ Missing Person Information System")
    st.markdown("Easily manage, update, and search missing person data.")

    menu = ["Add Person", "View All", "Mark Found", "Delete"]
    choice = st.sidebar.selectbox("Menu", menu)

    init_db()

    if choice == "Add Person":
        st.subheader("➕ Add New Missing Person")
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0, max_value=120)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        last_seen = st.text_input("Last Seen Location")
        contact = st.text_input("Contact Info")

        if st.button("Add"):
            if name and last_seen and contact:
                add_person(name, age, gender, last_seen, contact)
                st.success(f"{name} has been added to the missing persons list.")
            else:
                st.warning("Please fill in all required fields.")

    elif choice == "View All":
        st.subheader("📋 View All Records")
        df = get_all_persons()
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No records found.")

    elif choice == "Mark Found":
        st.subheader("✅ Mark Person as Found")
        df = get_all_persons()
        if not df.empty:
            found_id = st.selectbox("Select ID to Mark Found", df['id'])
            if st.button("Mark as Found"):
                mark_found(found_id)
                st.success(f"Person with ID {found_id} has been marked as found.")
        else:
            st.info("No missing persons available to update.")

    elif choice == "Delete":
        st.subheader("🗑️ Delete Record")
        df = get_all_persons()
        if not df.empty:
            delete_id = st.selectbox("Select ID to Delete", df['id'])
            if st.button("Delete"):
                delete_person(delete_id)
                st.warning(f"Person with ID {delete_id} has been deleted.")
        else:
            st.info("No records available to delete.")

if __name__ == '__main__':
    main()

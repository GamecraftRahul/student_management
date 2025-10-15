

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import errorcode

# ------------------------- CONFIGURE DATABASE -------------------------
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'RAHUL123',
    'database': 'student_db'
}

# Table definition used by the app (created if missing)
CREATE_TABLE_SQL = (
    "CREATE TABLE IF NOT EXISTS students ("
    " id INT AUTO_INCREMENT PRIMARY KEY,"
    " roll VARCHAR(50) NOT NULL UNIQUE,"
    " name VARCHAR(255) NOT NULL,"
    " age INT,"
    " gender VARCHAR(10),"
    " course VARCHAR(255)"
    ") ENGINE=InnoDB"
)

# ------------------------- DATABASE HELPERS -------------------------

def get_connection(config=None):
    cfg = config or DB_CONFIG
    try:
        conn = mysql.connector.connect(**cfg)
        return conn
    except mysql.connector.Error as err:
        # For initial creation of database, user might not have the db created yet
        raise


def ensure_database_and_table():
    # Ensure database exists, then ensure students table exists
    tmp_cfg = DB_CONFIG.copy()
    db_name = tmp_cfg.pop('database')
    try:
        # Connect without database to create db if needed
        conn = mysql.connector.connect(host=tmp_cfg['host'], user=tmp_cfg['user'], password=tmp_cfg['password'])
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET 'utf8mb4'")
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror('DB Error', f'Error creating database: {err}')
        return False

    # Now connect to the database and create table if needed
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(CREATE_TABLE_SQL)
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        messagebox.showerror('DB Error', f'Error creating table: {err}')
        return False


# ------------------------- CRUD OPERATIONS -------------------------

def add_student(roll, name, age, gender, course):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO students (roll, name, age, gender, course) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (roll, name, age or None, gender, course))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.IntegrityError as err:
        messagebox.showerror('Error', f'Roll already exists or integrity error: {err}')
        return False
    except mysql.connector.Error as err:
        messagebox.showerror('Error', f'Database error: {err}')
        return False


def update_student(student_id, roll, name, age, gender, course):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "UPDATE students SET roll=%s, name=%s, age=%s, gender=%s, course=%s WHERE id=%s"
        cursor.execute(sql, (roll, name, age or None, gender, course, student_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        messagebox.showerror('Error', f'Database error: {err}')
        return False


def delete_student(student_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM students WHERE id=%s"
        cursor.execute(sql, (student_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        messagebox.showerror('Error', f'Database error: {err}')
        return False


def fetch_students(filter_by=None, value=None):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        base = "SELECT id, roll, name, age, gender, course FROM students"
        if filter_by and value:
            sql = base + f" WHERE {filter_by} LIKE %s ORDER BY id DESC"
            cursor.execute(sql, (f"%{value}%",))
        else:
            sql = base + " ORDER BY id DESC"
            cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror('Error', f'Database error: {err}')
        return []


# ------------------------- GUI -------------------------

class StudentApp:
    def __init__(self, root):
        self.root = root
        root.title('Student Management System')
        root.geometry('900x550')
        root.resizable(False, False)

        # Top Frame - form
        form_frame = ttk.LabelFrame(root, text='Student Details')
        form_frame.place(x=10, y=10, width=880, height=170)

        # Variables
        self.var_id = tk.StringVar()
        self.var_roll = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_age = tk.StringVar()
        self.var_gender = tk.StringVar()
        self.var_course = tk.StringVar()
        self.var_search = tk.StringVar()
        self.var_search_by = tk.StringVar(value='name')

        # Labels and entries
        ttk.Label(form_frame, text='Roll:').place(x=10, y=10)
        self.entry_roll = ttk.Entry(form_frame, textvariable=self.var_roll, width=30)
        self.entry_roll.place(x=80, y=10)

        ttk.Label(form_frame, text='Name:').place(x=420, y=10)
        self.entry_name = ttk.Entry(form_frame, textvariable=self.var_name, width=30)
        self.entry_name.place(x=480, y=10)

        ttk.Label(form_frame, text='Age:').place(x=10, y=50)
        self.entry_age = ttk.Entry(form_frame, textvariable=self.var_age, width=30)
        self.entry_age.place(x=80, y=50)

        ttk.Label(form_frame, text='Gender:').place(x=420, y=50)
        self.combo_gender = ttk.Combobox(form_frame, textvariable=self.var_gender, state='readonly', values=['Male', 'Female', 'Other'], width=28)
        self.combo_gender.place(x=480, y=50)

        ttk.Label(form_frame, text='Course:').place(x=10, y=90)
        self.entry_course = ttk.Entry(form_frame, textvariable=self.var_course, width=30)
        self.entry_course.place(x=80, y=90)

        # Buttons
        btn_add = ttk.Button(form_frame, text='Add', command=self.add_student)
        btn_add.place(x=480, y=90, width=80)
        btn_update = ttk.Button(form_frame, text='Update', command=self.update_student)
        btn_update.place(x=570, y=90, width=80)
        btn_delete = ttk.Button(form_frame, text='Delete', command=self.delete_student)
        btn_delete.place(x=660, y=90, width=80)
        btn_clear = ttk.Button(form_frame, text='Clear', command=self.clear_form)
        btn_clear.place(x=750, y=90, width=80)

        # Search area
        ttk.Label(form_frame, text='Search:').place(x=10, y=130)
        self.entry_search = ttk.Entry(form_frame, textvariable=self.var_search, width=30)
        self.entry_search.place(x=80, y=130)
        self.combo_search_by = ttk.Combobox(form_frame, textvariable=self.var_search_by, state='readonly', values=['name', 'roll', 'course'], width=12)
        self.combo_search_by.place(x=340, y=130)
        btn_search = ttk.Button(form_frame, text='Search', command=self.search_students)
        btn_search.place(x=480, y=130, width=80)
        btn_refresh = ttk.Button(form_frame, text='Refresh', command=self.load_students)
        btn_refresh.place(x=570, y=130, width=80)

        # Treeview frame
        list_frame = ttk.LabelFrame(root, text='Students List')
        list_frame.place(x=10, y=190, width=880, height=350)

        columns = ('id', 'roll', 'name', 'age', 'gender', 'course')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        self.tree.heading('id', text='ID')
        self.tree.column('id', width=50, anchor='center')
        self.tree.heading('roll', text='Roll')
        self.tree.column('roll', width=100)
        self.tree.heading('name', text='Name')
        self.tree.column('name', width=200)
        self.tree.heading('age', text='Age')
        self.tree.column('age', width=50, anchor='center')
        self.tree.heading('gender', text='Gender')
        self.tree.column('gender', width=80, anchor='center')
        self.tree.heading('course', text='Course')
        self.tree.column('course', width=250)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind selection
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # Load initial data
        self.load_students()

    # ---------------- GUI actions ----------------
    def clear_form(self):
        self.var_id.set('')
        self.var_roll.set('')
        self.var_name.set('')
        self.var_age.set('')
        self.var_gender.set('')
        self.var_course.set('')

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']
            # id, roll, name, age, gender, course
            self.var_id.set(values[0])
            self.var_roll.set(values[1])
            self.var_name.set(values[2])
            self.var_age.set(values[3])
            self.var_gender.set(values[4])
            self.var_course.set(values[5])

    def add_student(self):
        roll = self.var_roll.get().strip()
        name = self.var_name.get().strip()
        age = self.var_age.get().strip()
        gender = self.var_gender.get().strip()
        course = self.var_course.get().strip()

        if not roll or not name:
            messagebox.showwarning('Validation', 'Roll and Name are required')
            return

        if age:
            try:
                age = int(age)
            except ValueError:
                messagebox.showwarning('Validation', 'Age must be a number')
                return

        ok = add_student(roll, name, age, gender, course)
        if ok:
            messagebox.showinfo('Success', 'Student added successfully')
            self.clear_form()
            self.load_students()

    def update_student(self):
        student_id = self.var_id.get()
        if not student_id:
            messagebox.showwarning('Select', 'Select a student to update')
            return
        roll = self.var_roll.get().strip()
        name = self.var_name.get().strip()
        age = self.var_age.get().strip()
        gender = self.var_gender.get().strip()
        course = self.var_course.get().strip()

        if not roll or not name:
            messagebox.showwarning('Validation', 'Roll and Name are required')
            return

        if age:
            try:
                age = int(age)
            except ValueError:
                messagebox.showwarning('Validation', 'Age must be a number')
                return

        ok = update_student(student_id, roll, name, age, gender, course)
        if ok:
            messagebox.showinfo('Success', 'Student updated successfully')
            self.clear_form()
            self.load_students()

    def delete_student(self):
        student_id = self.var_id.get()
        if not student_id:
            messagebox.showwarning('Select', 'Select a student to delete')
            return
        if messagebox.askyesno('Confirm', 'Are you sure you want to delete this student?'):
            ok = delete_student(student_id)
            if ok:
                messagebox.showinfo('Success', 'Student deleted')
                self.clear_form()
                self.load_students()

    def load_students(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = fetch_students()
        for r in rows:
            self.tree.insert('', tk.END, values=(r['id'], r['roll'], r['name'], r['age'], r['gender'], r['course']))

    def search_students(self):
        query = self.var_search.get().strip()
        by = self.var_search_by.get().strip()
        if not query:
            messagebox.showwarning('Search', 'Enter text to search')
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = fetch_students(filter_by=by, value=query)
        for r in rows:
            self.tree.insert('', tk.END, values=(r['id'], r['roll'], r['name'], r['age'], r['gender'], r['course']))


# ------------------------- MAIN -------------------------

def main():
    try:
        ok = ensure_database_and_table()
        if not ok:
            return
    except Exception as e:
        messagebox.showerror('Error', f'Error ensuring DB/table: {e}')
        return

    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()

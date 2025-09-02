from tkinter import *
import mysql.connector
from functools import partial
from tkinter import ttk, messagebox
from tkinter import filedialog
import csv
import matplotlib.pyplot as plt
class ExpenseTracker:
    def __init__(self):
        self.db = self.connect_to_db()
        self.cursor = self.db.cursor()
        self.current_user_id = None
        self.login_window()

    def connect_to_db(self):
        try:
            return mysql.connector.connect(
                host="localhost",
                user="root",
                password="bala",
                database="expense_tracker"
            )
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Failed to connect: {e}")
            exit()

    def login_window(self):
        self.login_screen = Tk()
        self.login_screen.title("Login")
        self.login_screen.geometry("460x220")
        self.login_screen.config(bg="white")
        self.login_screen.resizable(False, False)

        Label(self.login_screen, text="Username: ", font=("consolas", 15, "bold"), bg="white").place(x=20, y=30)
        Label(self.login_screen, text="Password: ", font=("consolas", 15, "bold"), bg="white").place(x=20, y=70)

        self.username_entry = Entry(self.login_screen)
        self.username_entry.place(x=150, y=33)

        self.password_entry = Entry(self.login_screen, show="*")
        self.password_entry.place(x=150, y=73)

        Button(self.login_screen, text="Login", font=("consolas", 12), cursor="hand2", bg="green", fg="white",
               command=self.login).place(x=70, y=120, width=100)
        Button(self.login_screen, text="Register", font=("consolas", 12), cursor="hand2", bg="red", fg="white",
               command=self.register_user).place(x=180, y=120, width=100)

        self.login_screen.mainloop()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Username and password cannot be empty!")
            return

        query = "SELECT id FROM users WHERE username = %s AND password = %s"
        self.cursor.execute(query, (username, password))
        result = self.cursor.fetchone()

        if result:
            self.current_user_id = result[0]
            messagebox.showinfo("Success", "Login successful!")
            self.login_screen.destroy()
            self.main_window()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def register_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "All fields are required!")
            return

        try:
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            self.cursor.execute(query, (username, password))
            self.db.commit()
            messagebox.showinfo("Success", "User registered successfully!")
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))

    def main_window(self):
        self.window = Tk()
        self.window.title("Expense Tracker")
        self.window.geometry("780x400")
        self.window.config(bg="white")
        self.window.resizable(False, False)

        self.create_expense_form()
        self.create_expense_table()

        self.window.mainloop()

    def create_expense_form(self):
        Label(self.window, text="Expense Name", font=("Consolas", 14), bg="white").place(x=20, y=20)
        Label(self.window, text="Amount", font=("Consolas", 14), bg="white").place(x=240, y=20)
        Label(self.window, text="Date", font=("Consolas", 14), bg="white").place(x=400, y=20)

        self.expense_name = Entry(self.window)
        self.expense_name.place(x=20, y=50)

        self.amount = Entry(self.window)
        self.amount.place(x=240, y=50, width=120)

        self.date = Entry(self.window)
        self.date.place(x=400, y=50, width=120)

        Button(self.window, text="Add Expense", font=("Consolas", 10), bg="green", fg="white",
               command=self.add_expense).place(x=550, y=40)

        Button(self.window, text="Logout", font=("consolas", 10), bg="yellow",
               command=self.logout).place(x=20, y=350)

        self.show_total_expense()
        # Visualize & Export buttons
        Button(self.window, text="Visualize", font=("consolas", 10), bg="blue", fg="white",
        command=self.visualize_expenses).place(x=550, y=340)

        Button(self.window, text="Export CSV", font=("consolas", 10), bg="purple", fg="white",
        command=self.export_expenses_csv).place(x=650, y=340)

        
    def create_expense_table(self):
        self.frame = Frame(self.window, bg="white")
        self.frame.place(x=20, y=90, width=740, height=200)

        self.columns = ('id', 'expense_name', 'amount', 'date')

        scroll_x = ttk.Scrollbar(self.frame, orient=HORIZONTAL)
        scroll_y = ttk.Scrollbar(self.frame, orient=VERTICAL)

        self.tree = ttk.Treeview(self.frame, columns=self.columns, height=200, yscrollcommand=scroll_y.set,
                                 xscrollcommand=scroll_x.set, selectmode="browse")

        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.config(command=self.tree.xview)
        scroll_y.config(command=self.tree.yview)

        self.tree.heading('id', text='ID')
        self.tree.heading('expense_name', text='Expense Name')
        self.tree.heading('amount', text='Amount')
        self.tree.heading('date', text='Date')

        self.tree['show'] = 'headings'
        self.tree.pack(fill=BOTH, expand=True)
        Button(self.window, text="Edit", font=("consolas", 10), bg="green", fg="white",
           cursor="hand2", command=self.edit_expense).place(x=20, y=300)

        Button(self.window, text="Delete", font=("consolas", 10), bg="red", fg="white",
           cursor="hand2", command=self.delete_expense).place(x=90, y=300)
       
        self.load_expenses()
    def edit_expense(self):
        x = self.tree.selection()
        if not x:  
            messagebox.showwarning("Selection Error", "Please select an expense to edit.")
            return
        y = self.tree.item(x)['values']
        if not y:
            messagebox.showwarning("Selection Error", "Invalid selection.")
            return
        query = "SELECT * FROM expenses WHERE id = %s"
        self.cursor.execute(query, (y[0],))
        row = self.cursor.fetchone()
        if row:
            self.clear_screen()
            self.get_new_data(row)

    def get_new_data(self, row):
        Label(self.window, text="Expense Name", font=("Consolas", 14, "bold"), bg="white").place(x=20,y=20)
        Label(self.window, text="Amount", font=("Consolas", 14, "bold"), bg="white").place(x=240,y=20)
        Label(self.window, text="Date", font=("Consolas", 14, "bold"), bg="white").place(x=400,y=20)

        self.new_expense_name = Entry(self.window)
        self.new_expense_name.insert(END, f"{row[2]}")
        self.new_expense_name.place(x=20, y=50)

        self.new_amount = Entry(self.window)
        self.new_amount.insert(END, f"{row[3]}")
        self.new_amount.place(x=240, y=50, width=120)

        self.new_date = Entry(self.window)
        self.new_date.insert(END, f"{row[4]}")
        self.new_date.place(x=400, y=50, width=120)

        Button(self.window, text="Submit", font=("Consolas", 10), bg="green", fg="white", cursor="hand2", command=partial(self.update_expense, row)).place(x=550, y=40)

    def update_expense(self, row):
        if self.new_expense_name.get() == "" or self.new_amount.get() == "" or self.new_date.get() == "":
            messagebox.showerror("Error!", "All fields are required", parent=self.window)
        else:
            query = "update expenses set expense_name=%s, amount=%s, date=%s where id=%s"
            self.cursor.execute(query, (self.new_expense_name.get(), self.new_amount.get(), self.new_date.get(), row[0],))
            self.db.commit()
            messagebox.showinfo("Successful", "Data has been updated")
            self.clear_screen()
            self.create_expense_form()
            self.create_expense_table()
            self.clear_expense_form()

    def delete_expense(self):
        x = self.tree.selection()
        if not x:  
            messagebox.showwarning("Selection Error", "Please select an expense to delete.")
            return

        y = self.tree.item(x)['values']
        if not y:  
            messagebox.showwarning("Selection Error", "Invalid selection.")
            return
        response = messagebox.askokcancel("Confirm Deletion", "Are you sure you want to delete this expense?")

        try:
            if response:
                query = "DELETE FROM expenses WHERE id = %s"
                self.cursor.execute(query, (y[0],))
                self.db.commit()
                
                messagebox.showinfo("Deleted", "Expense has been deleted.")
                self.clear_frame()
                self.create_expense_table()
                self.show_total_expense()
            else:
                messagebox.showinfo("Cancelled", "Deletion was cancelled.")
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))

    def load_expenses(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = "SELECT id, expense_name, amount, date FROM expenses WHERE user_id = %s"
        self.cursor.execute(query, (self.current_user_id,))
        results = self.cursor.fetchall()

        for expense in results:
            self.tree.insert('', 'end', values=expense)

    def add_expense(self):
        expense_name = self.expense_name.get()
        amount = self.amount.get()
        date = self.date.get()

        if not expense_name or not amount or not date:
            messagebox.showerror("Input Error", "All fields are required!")
            return

        try:
            query = "INSERT INTO expenses (user_id, expense_name, amount, date) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (self.current_user_id, expense_name, amount, date))
            self.db.commit()
            messagebox.showinfo("Success", "Expense added successfully!")
            self.load_expenses()
            self.show_total_expense()
            self.clear_expense_form()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", str(e))

    def show_total_expense(self):
        query = "SELECT SUM(amount) FROM expenses WHERE user_id = %s"
        self.cursor.execute(query, (self.current_user_id,))
        total_expense = self.cursor.fetchone()[0] or 0

        Label(self.window, text=f"Total: {total_expense}", font=("consolas", 15), bg="blue",
              fg="white").place(x=550, y=300)

    def clear_screen(self):
        for widget in self.window.winfo_children():
            widget.destroy()
    
    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def clear_expense_form(self):
        self.expense_name.delete(0, END)
        self.amount.delete(0, END)
        self.date.delete(0, END)

    def logout(self):
        self.window.destroy()
        self.current_user_id = None
        self.login_window()
    def export_expenses_csv(self):
        try:
            query = "SELECT id, expense_name, amount, date FROM expenses WHERE user_id = %s"
            self.cursor.execute(query, (self.current_user_id,))
            rows = self.cursor.fetchall()

            if not rows:
                messagebox.showinfo("No Data", "No expenses to export.")
                return

            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Save Expense Report As"
            )
            if not file_path:
                return  # user cancelled

            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Expense Name", "Amount", "Date"])
                writer.writerows(rows)

            messagebox.showinfo("Exported", f"Expenses exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
    def visualize_expenses(self):
        try:
            # Aggregate by expense name so we avoid any date-format issues
            query = """
                SELECT expense_name, SUM(amount)
                FROM expenses
                WHERE user_id = %s
                GROUP BY expense_name
                ORDER BY SUM(amount) DESC
            """
            self.cursor.execute(query, (self.current_user_id,))
            rows = self.cursor.fetchall()

            if not rows:
                messagebox.showinfo("No Data", "Add some expenses to visualize.")
                return

            names = [r[0] for r in rows]
            totals = [float(r[1]) for r in rows]

            plt.figure()
            plt.bar(names, totals)
            plt.xlabel("Expense Name")
            plt.ylabel("Total Amount")
            plt.title("Expenses by Name")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror("Visualization Error", str(e))



if __name__ == "__main__":
    ExpenseTracker()
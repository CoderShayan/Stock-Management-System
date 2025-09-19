#============================
# Stock Management System
#============================

import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# ---------------- Database Setup ----------------
conn = sqlite3.connect('stock.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT,
        quantity INTEGER
    )
''')
conn.commit()

edt_id = None  # track which row is being edited

# ---------------- Functions ----------------

# Add item function
def add_item():
    """Add a new item."""
    name = entry_name.get().strip()
    quantity = entry_quantity.get().strip()
    if name and quantity.isdigit():
        cursor.execute('INSERT INTO items (name, quantity) VALUES (?, ?)', (name, int(quantity)))
        conn.commit()
        messagebox.showinfo('Success', 'Item added successfully!')
        update_table()
        clear_entries()
    else:
        messagebox.showerror('Error', 'Please enter valid name and quantity!')

# Update table function
def update_table(search_text=""):
    """Refresh table with data from DB (supports search)."""
    for row in tree.get_children():
        tree.delete(row)

    if search_text:
        cursor.execute('SELECT * FROM items WHERE name LIKE ?', (f'%{search_text}%',))
    else:
        cursor.execute('SELECT * FROM items')

    rows = cursor.fetchall()
    for row in rows:
        tree.insert('', 'end', values=row)

    # update total stock count
    cursor.execute("SELECT SUM(quantity) FROM items")
    total = cursor.fetchone()[0]
    lbl_total.config(text=f"Total Stock: {total if total else 0}")

# Delete item function
def delete_item():
    """Delete selected item."""
    selected = tree.selection()
    if selected:
        item_id = tree.item(selected[0])['values'][0]
        cursor.execute('DELETE FROM items WHERE id=?', (item_id,))
        conn.commit()
        messagebox.showinfo('Success', 'Item deleted successfully!')
        update_table()
    else:
        messagebox.showerror('Error', 'Please select an item to delete!')

# Edit item function
def edit_item():
    """Load selected row into form for editing."""
    global edt_id
    selected = tree.selection()
    if selected:
        item_id, name, quantity = tree.item(selected[0])['values']
        entry_name.delete(0, tk.END)
        entry_name.insert(0, name)
        entry_quantity.delete(0, tk.END)
        entry_quantity.insert(0, quantity)
        edt_id = item_id
        btn_update.config(state=tk.NORMAL)
        btn_add.config(state=tk.DISABLED)
    else:
        messagebox.showerror('Error', 'Please select an item to edit!')

# Update item function
def update_item():
    """Update existing item."""
    global edt_id
    if edt_id is None:
        return
    name = entry_name.get().strip()
    quantity = entry_quantity.get().strip()
    if name and quantity.isdigit():
        cursor.execute('UPDATE items SET name=?, quantity=? WHERE id=?', (name, int(quantity), edt_id))
        conn.commit()
        messagebox.showinfo('Success', 'Item updated successfully!')
        update_table()
        clear_entries()
        btn_update.config(state=tk.DISABLED)
        btn_add.config(state=tk.NORMAL)
        edt_id = None
    else:
        messagebox.showerror('Error', 'Please enter valid name and quantity!')

# Clear form entries
def clear_entries():
    entry_name.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)

# Handle double-click on table row
def on_double_click(event):
    edit_item()

# Search items function
def search_items():
    search_text = entry_search.get().strip()
    update_table(search_text)

# Sort column function
def sort_column(col, reverse):
    """Sort the treeview by clicking column header."""
    data = [(tree.set(k, col), k) for k in tree.get_children('')]
    try:
        data.sort(key=lambda t: int(t[0]), reverse=reverse)
    except ValueError:
        data.sort(reverse=reverse)
    for index, (val, k) in enumerate(data):
        tree.move(k, '', index)
    tree.heading(col, command=lambda: sort_column(col, not reverse))

# Close DB connection on exit
def on_close():
    conn.close()
    window.destroy()

# ---------------- GUI Setup ----------------

window = tk.Tk()
window.title('Stock Management System')
window.geometry('500x450')

# --- Top Frame (form) ---
frame_form = tk.Frame(window, padx=10, pady=10)
frame_form.pack(fill='x')

tk.Label(frame_form, text='Name:').grid(row=0, column=0, sticky='w')
entry_name = tk.Entry(frame_form)
entry_name.grid(row=0, column=1, padx=5)

tk.Label(frame_form, text='Quantity:').grid(row=1, column=0, sticky='w')
entry_quantity = tk.Entry(frame_form)
entry_quantity.grid(row=1, column=1, padx=5)

# --- Buttons ---
btn_add = tk.Button(frame_form, text='Add Item', command=add_item)
btn_add.grid(row=2, column=0, pady=5)

btn_update = tk.Button(frame_form, text='Update Item', command=update_item, state=tk.DISABLED)
btn_update.grid(row=2, column=1, pady=5)

btn_edit = tk.Button(frame_form, text='Edit Selected', command=edit_item)
btn_edit.grid(row=3, column=0, pady=5)

btn_delete = tk.Button(frame_form, text='Delete Selected', command=delete_item)
btn_delete.grid(row=3, column=1, pady=5)

# --- Search Bar ---
frame_search = tk.Frame(window, padx=10, pady=5)
frame_search.pack(fill='x')
tk.Label(frame_search, text='Search:').pack(side='left')
entry_search = tk.Entry(frame_search)
entry_search.pack(side='left', padx=5)
btn_search = tk.Button(frame_search, text='Go', command=search_items)
btn_search.pack(side='left')

# --- Table ---
tree = ttk.Treeview(window, columns=('id', 'name', 'quantity'), show='headings', height=10)
tree.heading('id', text='ID', command=lambda: sort_column('id', False))
tree.heading('name', text='Name', command=lambda: sort_column('name', False))
tree.heading('quantity', text='Quantity', command=lambda: sort_column('quantity', False))

tree.column('id', width=50, anchor='center')
tree.column('name', width=250, anchor='w')
tree.column('quantity', width=100, anchor='center')

tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
tree.bind("<Double-1>", on_double_click)

# --- Footer (total stock) ---
lbl_total = tk.Label(window, text="Total Stock: 0", font=("Arial", 10, "bold"))
lbl_total.pack(pady=5)

update_table()

# --- Window close event ---
window.protocol("WM_DELETE_WINDOW", on_close)

window.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime

categories = [
    "Продукти", "Одяг", "Транспорт", "Розваги", "Здоров’я", "Навчання", "Благодійність",
    "Заробітна плата", "Інвестиційні надходження"
]

class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.init_main()
        self.db = DB()
        self.view_records()

    def init_main(self):
        toolbar = tk.Frame(bg='#d7d8e0', bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.add_img = tk.PhotoImage(file="add.gif")
        btn_open_dialog = tk.Button(toolbar, text='Додати позицію', command=self.open_dialog, bg='#d7d8e0', bd=0,
                                    compound=tk.TOP, image=self.add_img)
        btn_open_dialog.pack(side=tk.LEFT, padx=(175, 10))

        self.update_img = tk.PhotoImage(file='update.gif')
        btn_edit_dialog = tk.Button(toolbar, text='Редагувати', bg='#d7d8e0', bd=0, image=self.update_img,
                                    compound=tk.TOP, command=self.open_update_dialog)
        btn_edit_dialog.pack(side=tk.LEFT, padx=(10, 10))

        self.delete_img = tk.PhotoImage(file='delete.gif')
        btn_delete = tk.Button(toolbar, text='Видалити позицію', bg='#d7d8e0', bd=0, image=self.delete_img,
                               compound=tk.TOP, command=self.delete_records)
        btn_delete.pack(side=tk.LEFT, padx=(10, 10))

        self.search_img = tk.PhotoImage(file='search.gif')
        btn_search = tk.Button(toolbar, text='Пошук', bg='#d7d8e0', bd=0, image=self.search_img,
                               compound=tk.TOP, command=self.open_search_dialog)
        btn_search.pack(side=tk.LEFT, padx=(10, 10))

        self.refresh_img = tk.PhotoImage(file='refresh.gif')
        btn_refresh = tk.Button(toolbar, text='Оновити', bg='#d7d8e0', bd=0, image=self.refresh_img,
                                compound=tk.TOP, command=self.view_records)
        btn_refresh.pack(side=tk.LEFT, padx=(10, 10))

        self.tree = ttk.Treeview(self, columns=('ID', 'category', 'costs', 'total', 'comment', 'date'),
                                 height=15, show='headings')
        self.tree.column("ID", width=30, anchor=tk.CENTER)
        self.tree.column("category", width=250, anchor=tk.CENTER)
        self.tree.column("costs", width=150, anchor=tk.CENTER)
        self.tree.column("total", width=100, anchor=tk.CENTER)
        self.tree.column("comment", width=200, anchor=tk.CENTER)
        self.tree.column("date", width=100, anchor=tk.CENTER)

        self.tree.heading("ID", text='ID')
        self.tree.heading("category", text='Категорія')
        self.tree.heading("costs", text='Стаття доходу/витрати')
        self.tree.heading("total", text='Сума')
        self.tree.heading("comment", text='Комментарій')
        self.tree.heading("date", text='Дата')

        self.tree.pack(side=tk.LEFT)

        scroll = tk.Scrollbar(self, command=self.tree.yview)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scroll.set)

    def records(self, category, costs, total, comment, date):
        self.db.insert_data(category, costs, total, comment, date)
        self.view_records()

    def update_record(self, category, costs, total, comment, date):
        selection = self.tree.selection()
        if selection:
            formatted_date = date 
            self.db.c.execute('''UPDATE finance SET category=?, costs=?, total=?, comment=?, date=? WHERE ID=?''',
                          (category, costs, total, comment, formatted_date, self.tree.set(selection[0], '#1')))
            self.db.conn.commit()
            self.view_records()

    def view_records(self):
        self.db.c.execute('''SELECT * FROM finance''')
        [self.tree.delete(i) for i in self.tree.get_children()]
        for row in self.db.c.fetchall():
            self.tree.insert('', 'end', values=row)

    def delete_records(self):
        for selection_item in self.tree.selection():
            self.db.c.execute('''DELETE FROM finance WHERE id=?''', (self.tree.set(selection_item, '#1'),))
        self.db.conn.commit()
        self.view_records()

    def search_records(self, keyword=None, start_date=None, end_date=None):
        query = '''SELECT * FROM finance'''
        conditions = []
        params = []

        if keyword:
            conditions.append("category LIKE ?")
            params.append('%' + keyword + '%')
        if start_date and end_date:
            conditions.append("date BETWEEN ? AND ?")
            params.extend([start_date, end_date])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        self.db.c.execute(query, params)
        [self.tree.delete(i) for i in self.tree.get_children()]
        for row in self.db.c.fetchall():
            self.tree.insert('', 'end', values=row)

    def open_dialog(self):
        Child(self)

    def open_update_dialog(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_data = self.tree.item(selected_item, "values")
            UPDATE(item_data)

    def open_search_dialog(self):
        Search(self)

class Child(tk.Toplevel):
    def __init__(self, main):
        super().__init__(main)
        self.init_child()
        self.view = main

    def init_child(self):
        self.title('Додати доходи/витрати')
        self.geometry('400x270+400+300')
        self.resizable(False, False)

        label_description = tk.Label(self, text='Категорія:')
        label_description.place(x=50, y=50)
        label_select = tk.Label(self, text='Стаття доходу/витрати:')
        label_select.place(x=50, y=80)
        label_sum = tk.Label(self, text='Сума:')
        label_sum.place(x=50, y=110)

        self.label_comment = tk.Label(self, text='Комментарій:')
        self.label_comment.place(x=50, y=140)

        self.label_date = tk.Label(self, text='Дата:')
        self.label_date.place(x=50, y=170)

        self.entry_comment = ttk.Entry(self)
        self.entry_comment.place(x=200, y=140, width=150)

        self.combobox_category = ttk.Combobox(self, values=categories, state='readonly')
        self.combobox_category.place(x=200, y=50)

        self.combobox = ttk.Combobox(self, values=["Дохід", "Витрата"], state='readonly')
        self.combobox.current(0)
        self.combobox.place(x=200, y=80)

        self.entry_money = ttk.Entry(self)
        self.entry_money.place(x=200, y=110)

        self.entry_date = DateEntry(self, date_pattern='dd.mm.yyyy')
        self.entry_date.set_date(datetime.now())
        self.entry_date.place(x=200, y=170)

        btn_cancel = ttk.Button(self, text='Закрити', command=self.destroy)
        btn_cancel.place(x=300, y=200)

        self.btn_ok = ttk.Button(self, text='Додати')
        self.btn_ok.place(x=220, y=200)
        self.btn_ok.bind('<Button-1>', lambda event: self.validate())
        self.grab_set()
        self.focus_set()

    def validate(self):
        category = self.combobox_category.get()
        costs = self.combobox.get()
        total = self.entry_money.get()
        comment = self.entry_comment.get()
        date = self.entry_date.get()

        if not category or not costs or not total:
            messagebox.showerror("Помилка", "Всі поля повинні бути заповнені!")
            return

        try:
            float(total)
        except ValueError:
            messagebox.showerror("Помилка", "Сума має бути числом!")
            return

        self.view.records(category, costs, total, comment, date)
        self.destroy()

class Search(tk.Toplevel):
    def __init__(self, main):
        super().__init__(main)
        self.view = main
        self.init_search()

    def init_search(self):
        self.title('Пошук по записах')
        self.geometry('400x220+400+300')
        self.resizable(False, False)

        self.search_label = tk.Label(self, text='Ключове слово:')
        self.search_label.place(x=50, y=20)
        self.search_entry = ttk.Entry(self)
        self.search_entry.place(x=200, y=20, width=150)

        self.date_label = tk.Label(self, text='Дата початку:')
        self.date_label.place(x=50, y=60)
        self.start_date_entry = DateEntry(self, date_pattern='dd.mm.yyyy')
        self.start_date_entry.place(x=200, y=60)

        self.end_date_label = tk.Label(self, text='Дата завершення:')
        self.end_date_label.place(x=50, y=100)
        self.end_date_entry = DateEntry(self, date_pattern='dd.mm.yyyy')
        self.end_date_entry.place(x=200, y=100)

        self.btn_search = ttk.Button(self, text='Пошук')
        self.btn_search.place(x=220, y=140)
        self.btn_search.bind('<Button-1>', lambda event: self.search())
        
        self.btn_cancel = ttk.Button(self, text='Закрити', command=self.destroy)
        self.btn_cancel.place(x=300, y=140)
        
        self.grab_set()
        self.focus_set()

    def search(self):
        keyword = self.search_entry.get()
        start_date = self.start_date_entry.get_date().strftime('%d.%m.%Y')
        end_date = self.end_date_entry.get_date().strftime('%d.%m.%Y')
        self.view.search_records(keyword, start_date, end_date)
        self.destroy()

class UPDATE(tk.Toplevel):
    def __init__(self, item_data):
        super().__init__()
        self.init_update(item_data)

    def init_update(self, item_data):
        self.title('Редагувати запис')
        self.geometry('400x270+400+300')
        self.resizable(False, False)

        label_description = tk.Label(self, text='Категорія:')
        label_description.place(x=50, y=50)
        label_select = tk.Label(self, text='Стаття доходу/витрати:')
        label_select.place(x=50, y=80)
        label_sum = tk.Label(self, text='Сума:')
        label_sum.place(x=50, y=110)

        self.label_comment = tk.Label(self, text='Комментарій:')
        self.label_comment.place(x=50, y=140)

        self.label_date = tk.Label(self, text='Дата:')
        self.label_date.place(x=50, y=170)

        self.entry_comment = ttk.Entry(self)
        self.entry_comment.place(x=200, y=140, width=150)
        self.entry_comment.insert(0, item_data[4])

        self.combobox_category = ttk.Combobox(self, values=categories, state='readonly')
        self.combobox_category.place(x=200, y=50)
        self.combobox_category.set(item_data[1])

        self.combobox = ttk.Combobox(self, values=["Дохід", "Витрата"], state='readonly')
        self.combobox.place(x=200, y=80)
        self.combobox.set(item_data[2])

        self.entry_money = ttk.Entry(self)
        self.entry_money.place(x=200, y=110)
        self.entry_money.insert(0, item_data[3])

        self.entry_date = DateEntry(self, date_pattern='dd.mm.yyyy')
        self.entry_date.place(x=200, y=170)
        self.entry_date.set_date(datetime.strptime(item_data[5], '%d.%m.%Y'))

        btn_cancel = ttk.Button(self, text='Закрити', command=self.destroy)
        btn_cancel.place(x=300, y=200)

        self.btn_ok = ttk.Button(self, text='Зберегти', command=self.update_record)
        self.btn_ok.place(x=220, y=200)

        self.item_id = item_data[0]

    def update_record(self):
        category = self.combobox_category.get()
        costs = self.combobox.get()
        total = self.entry_money.get()
        comment = self.entry_comment.get()
        date = self.entry_date.get_date().strftime('%d.%m.%Y')

        if not category or not costs or not total:
            messagebox.showerror("Помилка", "Всі поля повинні бути заповнені!")
            return

        try:
            float(total)
        except ValueError:
            messagebox.showerror("Помилка", "Сума має бути числом!")
            return

        main_app.update_record(category, costs, total, comment, date)
        self.destroy()

class DB:
    def __init__(self):
        self.conn = sqlite3.connect('finance.db')
        self.c = self.conn.cursor()
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS finance (id integer primary key, category text, costs text, total real, comment text, date text)''')
        self.conn.commit()

    def insert_data(self, category, costs, total, comment, date):
        self.c.execute('''INSERT INTO finance(category, costs, total, comment, date) VALUES (?, ?, ?, ?, ?)''',
                       (category, costs, total, comment, date))
        self.conn.commit()

if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    app.pack()
    root.title("Домашня бухгалтерія")
    root.geometry("850x450+300+200")
    root.resizable(False, False)
    main_app = app  
    root.mainloop()


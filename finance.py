import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime

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

        self.tree = ttk.Treeview(self, columns=('ID', 'description', 'costs', 'total', 'comment', 'date'),
                                 height=15, show='headings')
        self.tree.column("ID", width=30, anchor=tk.CENTER)
        self.tree.column("description", width=250, anchor=tk.CENTER)
        self.tree.column("costs", width=150, anchor=tk.CENTER)
        self.tree.column("total", width=100, anchor=tk.CENTER)
        self.tree.column("comment", width=200, anchor=tk.CENTER)
        self.tree.column("date", width=100, anchor=tk.CENTER)

        self.tree.heading("ID", text='ID')
        self.tree.heading("description", text='Найменування')
        self.tree.heading("costs", text='Стаття доходу/витрати')
        self.tree.heading("total", text='Сума')
        self.tree.heading("comment", text='Комментарій')
        self.tree.heading("date", text='Дата')

        self.tree.pack(side=tk.LEFT)

        scroll = tk.Scrollbar(self, command=self.tree.yview)
        scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scroll.set)

    def records(self, description, costs, total, comment, date):
        self.db.insert_data(description, costs, total, comment, date)
        self.view_records()

    def update_record(self, description, costs, total, comment, date):
        selection = self.tree.selection()
        if selection:
            self.db.c.execute('''UPDATE finance SET description=?, costs=?, total=?, comment=?, date=? WHERE ID=?''',
                           (description, costs, total, comment, date, self.tree.set(selection[0], '#1')))
            self.db.conn.commit()
            self.view_records()

    def view_records(self):
        self.db.c.execute('''SELECT * FROM finance''')
        [self.tree.delete(i) for i in self.tree.get_children()]
        for row in self.db.c.fetchall():
            if len(row) >= 6:
                self.tree.insert('', 'end', values=(row[0], row[1], row[2], row[3], row[4], row[5]))
            else:
                pass

    def delete_records(self):
        for selection_item in self.tree.selection():
            self.db.c.execute('''DELETE FROM finance WHERE id=?''', (self.tree.set(selection_item, '#1'),))
        self.db.conn.commit()
        self.view_records()

    def search_records(self, search_query):
        date_format = "%d.%m"
        try:
                search_date = datetime.strptime(search_query, date_format).strftime("%d.%m")
        except ValueError:
            search_date = None
        if search_date is not None:
            self.db.c.execute('''SELECT * FROM finance WHERE date LIKE ?''', ('%'+search_date+'%',))
        else:
            self.db.c.execute('''SELECT * FROM finance WHERE description LIKE ?''', ('%'+search_query+'%',))

        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.db.c.fetchall()]


    def open_dialog(self):
        Child()

    def open_update_dialog(self):
        UPDATE()

    def open_search_dialog(self):
        Search()


class Child(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.init_child()
        self.view = app

    def init_child(self):
        self.title('Додати доходи/витрати')
        self.geometry('400x230+400+300')
        self.resizable(False, False)

        label_description = tk.Label(self, text='Найменуванняе:')
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

        self.entry_description = ttk.Entry(self)
        self.entry_description.place(x=200, y=50)

        self.entry_money = ttk.Entry(self)
        self.entry_money.place(x=200, y=110)

        self.entry_date = ttk.Entry(self)
        self.entry_date.place(x=200, y=170)

        self.combobox = ttk.Combobox(self, values=[u"Дохід", u"Витрата"])
        self.combobox.current(0)
        self.combobox.place(x=200, y=80)

        btn_cancel = ttk.Button(self, text='Закрити', command=self.destroy)
        btn_cancel.place(x=300, y=200)

        self.btn_ok = ttk.Button(self, text='Додати')
        self.btn_ok.place(x=220, y=200)
        self.btn_ok.bind('<Button-1>', lambda event: self.view.records(self.entry_description.get(),
                                                                        self.combobox.get(),
                                                                        self.entry_money.get(),
                                                                        self.entry_comment.get(),
                                                                        self.entry_date.get()))
        self.grab_set()
        self.focus_set()
        

class UPDATE(Child):
    def __init__(self):
        super().__init__()
        self.init_edit()
        self.view = app
        self.db = DB
        row = self.db.c.fetchone()
        if row:
            self.default_data(row)

    def init_edit(self):
        self.title('Редагувати позицію')
        btn_edit = ttk.Button(self, text='Редагувати')
        btn_edit.place(x=205, y=200)
        btn_edit.bind('<Button-1>', lambda event: self.view.update_record(self.entry_description.get(),
                                                                          self.combobox.get(),
                                                                          self.entry_money.get(),
                                                                          self.entry_comment.get(),
                                                                          self.entry_date.get()))
        self.btn_ok.destroy()

    def default_data(self, row):
        self.entry_description.insert(0, row[1])
        if row[2] != 'Дохід':
            self.combobox.current(1)
        self.entry_money.insert(0, row[3])
        self.entry_comment.insert(0, row[4])
        self.entry_date.insert(0, row[5])

class Search(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.init_search()
        self.view = app

    def init_search(self):
        self.title('Пошук')
        self.geometry('300x100+400+300')
        self.resizable(False, False)

        lable_search = tk.Label(self, text='Пошук')
        lable_search.place(x=50, y=20)

        self.entry_search = ttk.Entry(self)
        self.entry_search.place(x=105, y=20, width=150)

        btn_cancel = ttk.Button(self, text='Закрити', command=self.destroy)
        btn_cancel.place(x=185, y=50)
        
        btn_search = ttk.Button(self, text='Поиск')
        btn_search.place(x=105, y=50)
        btn_search.bind('<Button-1>', lambda event: self.view.search_records(self.entry_search.get()))
        btn_search.bind('<Button-1>', lambda event: self.destroy(), add='+')


class DB:
    def __init__(self):
        self.conn = sqlite3.connect('finance.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS finance (id INTEGER PRIMARY KEY,
                                                               description TEXT,
                                                               costs TEXT,
                                                               total REAL,
                                                               comment TEXT,
                                                               date TEXT)''')
        self.conn.commit()

    def insert_data(self, description, costs, total, comment, date):
        self.c.execute('''INSERT INTO finance(description, costs, total, comment, date) VALUES (?, ?, ?, ?, ?)''',
                       (description, costs, total, comment, date))
        self.conn.commit()

    def search_records(self, search_query):
        date_format = "%d.%m"
        try:
            search_date = datetime.strptime(search_query, date_format).strftime("%d.%m")
        except ValueError:
            search_date = None

        self.c.execute('''SELECT * FROM finance WHERE description LIKE ? OR date LIKE ?''', ('%'+search_query+'%', '%'+search_date+'%'))
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in self.c.fetchall()]


if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    app.pack()
    root.title("Домашні фінанси")
    root.geometry("860x450+300+200")
    root.resizable(False, False)
    root.mainloop()


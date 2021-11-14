import tkinter as Tk

from model import Model
from view import View

class Controller:
    def __init__(self):
        self.root = Tk.Tk()
        self.model = Model()
        self.view = View(self.root, self)

    def run(self):
        self.root.title("EPU Accounting")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = 900
        height = 500
        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)
        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))
        self.root.resizable(0, 0)
        self.root.deiconify()
        self.root.mainloop()

    def create(self, record):
        fetch = self.model.create(record)
        # todo: check for errors
        self.view.create_done()
        self.view.update_table(fetch)

    def read(self):
        fetch = self.model.read()
        self.view.read_done()
        self.view.update_table(fetch)

    def update(self, entry_id, first_name, last_name):
        fetch = self.model.update(entry_id, first_name, last_name)
        self.view.update_done()
        self.view.update_table(fetch)

    def delete(self, entry_id, list_item):
        self.model.delete(entry_id)
        self.view.delete_done()
        self.view.remove_from_table(list_item)

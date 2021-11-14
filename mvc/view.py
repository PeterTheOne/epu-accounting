#import tkinter as Tk
from tkinter import *
import tkinter.messagebox as tkMessageBox

from views.side_panel import SidePanel
from views.records_table import RecordsTable


class View:
    def __init__(self, root, controller):
        self.root = root
        self.frame = Frame(root)
        self.controller = controller

        #==================================FRAME==============================================
        Top = Frame(root, width=900, height=450)
        Top.pack(side=TOP, fill=BOTH, expand=1)
        Bottom = Frame(root, width=900, height=50, bd=4, relief="raise")
        Bottom.pack(side=BOTTOM, fill=X)

        Left = Frame(Top, width=300, height=450, bd=4, relief="raise")
        Left.pack(side=LEFT, fill=Y)
        Right = Frame(Top, width=600, height=450, bd=4, relief="raise")
        Right.pack(side=RIGHT, fill=BOTH, expand=1)

        Forms = Frame(Left, width=300, height=350)
        Forms.pack(side=TOP, fill=BOTH, expand=1)
        Buttons = Frame(Left, width=300, height=100)
        Buttons.pack(side=BOTTOM, fill=X)

        #==================================SIDE PANEL=========================================
        self.sidepanel = SidePanel(root, Forms, Buttons)
        self.sidepanel.btn_create.config(command=self.create)
        self.sidepanel.btn_update.config(command=self.update)

        #==================================TABLE==============================================
        self.recordstable = RecordsTable(root, Right)
        self.recordstable.tree.bind('<Double-Button-1>', self.select) # double click
        self.recordstable.btn_read.config(command=self.read)
        self.recordstable.btn_delete.config(command=self.delete)

        #==================================STATUS=============================================
        self.txt_result = Label(Bottom)
        self.txt_result.pack(side=LEFT)
        self.btn_exit = Button(Bottom, width=10, text="Exit", command=self.exit)
        self.btn_exit.pack(side=RIGHT)

    def select(self, event):
        list_item, record = self.recordstable.get_selected_item()
        self.sidepanel.fill_form(record)
        self.recordstable.btn_read.config(state=DISABLED)
        self.recordstable.btn_delete.config(state=DISABLED)

    def create(self, event=None):
        if self.sidepanel.is_form_valid():
            self.txt_result.config(text="Please complete the required field!", fg="red")
        else:
            self.controller.create(self.sidepanel.get_current_record())

    def create_done(self):
        self.sidepanel.clear_form()
        self.recordstable.btn_read.config(state=NORMAL)
        self.recordstable.btn_delete.config(state=NORMAL)
        self.txt_result.config(text="Added an entry!", fg="green")

    def read(self, event=None):
        self.controller.read()

    def read_done(self):
        self.txt_result.config(text="Successfully read the data from database", fg="black")

    def update(self, event=None):
        self.controller.update(self.sidepanel.entry_id, self.sidepanel.get_current_record())

    def update_done(self):
        self.sidepanel.clear_form()
        self.recordstable.btn_read.config(state=NORMAL)
        self.recordstable.btn_delete.config(state=NORMAL)
        self.txt_result.config(text="Successfully updated the data", fg="black")

    def delete(self, event=None):
        if not self.recordstable.tree.selection():
            self.txt_result.config(text="Please select an item first", fg="red")
        else:
            result = tkMessageBox.askquestion('Python: Simple CRUD Applition', 'Are you sure you want to delete this record?', icon="warning")
            if result == 'yes':
                list_item, entry = self.recordstable.get_selected_item()
                self.controller.delete(entry.entry_id, list_item)

    def delete_done(self):
        self.txt_result.config(text="Successfully deleted the data", fg="black")

    def exit(self, event=None):
        result = tkMessageBox.askquestion('Python: Simple CRUD Applition', 'Are you sure you want to exit?', icon="warning")
        if result == 'yes':
            self.root.destroy()
            exit()

    def update_table(self, fetch):
        self.recordstable.update(fetch)

    def remove_from_table(self, id):
        self.recordstable.tree.delete(id)

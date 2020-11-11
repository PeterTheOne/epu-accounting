#import tkinter as Tk
from tkinter import *
import tkinter.ttk as ttk

from models.Member import Member


class RecordsTable():
    def __init__(self, root, Right):
        TableTop = Frame(Right, width=600, height=400)
        TableTop.pack(side=TOP, fill=BOTH, expand=1)
        TableBottom = Frame(Right, width=600, height=50)
        TableBottom.pack(side=BOTTOM, fill=X)

        scrollbary = Scrollbar(TableTop, orient=VERTICAL)
        scrollbarx = Scrollbar(TableTop, orient=HORIZONTAL)
        #self.tree = ttk.Treeview(Right, columns=("ID", "Firstname", "Lastname"), selectmode="extended", height=350, yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
        self.tree = ttk.Treeview(TableTop, columns=("ID", "Firstname", "Lastname"), selectmode="extended", yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
        scrollbary.config(command=self.tree.yview)
        scrollbary.pack(side=RIGHT, fill=Y)
        scrollbarx.config(command=self.tree.xview)
        scrollbarx.pack(side=BOTTOM, fill=X)
        self.tree.heading('ID', text="ID", anchor=W)
        self.tree.heading('Firstname', text="Firstname", anchor=W)
        self.tree.heading('Lastname', text="Lastname", anchor=W)
        self.tree.column('#0', stretch=NO, minwidth=0, width=0)
        self.tree.column('#1', stretch=NO, minwidth=0, width=40)
        self.tree.column('#2', stretch=NO, minwidth=0, width=80)
        self.tree.column('#3', stretch=NO, minwidth=0, width=120)
        self.tree.pack(side=LEFT, fill=BOTH, expand=1)

        self.btn_read = Button(TableBottom, width=10, text="Read")
        self.btn_read.pack(side=LEFT)
        self.btn_delete = Button(TableBottom, width=10, text="Delete")
        self.btn_delete.pack(side=RIGHT)

    def update(self, fetch):
        self.tree.delete(*self.tree.get_children())
        for data in fetch:
            self.tree.insert('', 'end', values=(data[0], data[1], data[2]))

    def get_selected_item(self):
        list_item = self.tree.focus()
        contents = self.tree.item(list_item)
        values = contents['values']
        member = Member(member_id=values[0], first_name=values[1], last_name=values[2])
        return list_item, member

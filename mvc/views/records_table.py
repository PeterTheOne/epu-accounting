#import tkinter as Tk
from tkinter import *
import tkinter.ttk as ttk

from models.Record import Record


class RecordsTable():
    def __init__(self, root, Right):
        TableTop = Frame(Right, width=600, height=400)
        TableTop.pack(side=TOP, fill=BOTH, expand=1)
        TableBottom = Frame(Right, width=600, height=50)
        TableBottom.pack(side=BOTTOM, fill=X)

        scrollbary = Scrollbar(TableTop, orient=VERTICAL)
        scrollbarx = Scrollbar(TableTop, orient=HORIZONTAL)
        self.tree = ttk.Treeview(TableTop, columns=("ID", "Account", "Accounting No", "Accounting Date", "Status", "Amount", "Contra Name", "Subject", "Comment", "Text"), selectmode="extended", yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
        scrollbary.config(command=self.tree.yview)
        scrollbary.pack(side=RIGHT, fill=Y)
        scrollbarx.config(command=self.tree.xview)
        scrollbarx.pack(side=BOTTOM, fill=X)
        self.tree.heading('ID', text="ID", anchor=W)
        self.tree.heading('Account', text="Account", anchor=W)
        self.tree.heading('Accounting No', text="Accounting No", anchor=W)
        self.tree.heading('Accounting Date', text="Accounting Date", anchor=W)
        self.tree.heading('Status', text="Status", anchor=W)
        self.tree.heading('Amount', text="Amount", anchor=W)
        self.tree.heading('Contra Name', text="Contra Name", anchor=W)
        self.tree.heading('Subject', text="Subject", anchor=W)
        self.tree.heading('Comment', text="Comment", anchor=W)
        self.tree.heading('Text', text="Text", anchor=W)
        self.tree.column('#0', stretch=NO, minwidth=0, width=0)
        self.tree.column('#1', stretch=NO, minwidth=0, width=40) # ID
        self.tree.column('#2', stretch=NO, minwidth=0, width=100)
        self.tree.column('#3', stretch=NO, minwidth=0, width=80)
        self.tree.column('#4', stretch=NO, minwidth=0, width=140)
        self.tree.column('#5', stretch=NO, minwidth=0, width=140)
        self.tree.column('#6', stretch=NO, minwidth=0, width=140)
        self.tree.column('#7', stretch=NO, minwidth=0, width=140)
        self.tree.column('#8', stretch=NO, minwidth=0, width=140)
        self.tree.column('#9', stretch=NO, minwidth=0, width=140)
        self.tree.column('#10', stretch=NO, minwidth=0, width=140)
        self.tree.pack(side=LEFT, fill=BOTH, expand=1)

        self.btn_read = Button(TableBottom, width=10, text="Read")
        self.btn_read.pack(side=LEFT)
        self.btn_delete = Button(TableBottom, width=10, text="Delete")
        self.btn_delete.pack(side=RIGHT)

    def update(self, fetch):
        self.tree.delete(*self.tree.get_children())
        for data in fetch:
            self.tree.insert('', 'end', values=(
                data[0], # ID
                data[2], # Account
                data[3], # Accounting No
                data[4], # Accounting Date
                data[5], # Status
                data[10], # Amount
                data[15], # Contra Name
                data[12], # Subject
                data[14], # Comment
                data[15], # Text
                data[6] # ?
            ))

    def get_selected_item(self):
        list_item = self.tree.focus()
        contents = self.tree.item(list_item)
        values = contents['values']
        record = Record(
            entry_id=values[0],
            account=values[1],
            accounting_no=values[2],
            accounting_date=values[3],
            status=values[4],
            amount=values[5],
            contra_name=values[6],
            subject=values[7],
            comment=values[8],
            text=values[9]
        )
        return list_item, record

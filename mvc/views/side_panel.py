#import tkinter as Tk
from tkinter import *

from models.Record import Record

class SidePanel():
    def __init__(self, root, Forms, Buttons):
        self.entry_id = StringVar()
        self.account = StringVar()
        self.accounting_no = StringVar()
        self.accounting_date = StringVar()
        self.status = StringVar()
        self.amount = StringVar()
        self.contra_name = StringVar()
        self.subject = StringVar()
        self.comment = StringVar()
        self.text = StringVar()

        #==================================LABELS======================================
        account = Label(Forms, text="account", font=('arial', 14), bd=15)
        account.grid(row=0, sticky="e")
        accounting_no = Label(Forms, text="accounting_no", font=('arial', 14), bd=15)
        accounting_no.grid(row=1, sticky="e")
        accounting_date = Label(Forms, text="accounting_date", font=('arial', 14), bd=15)
        accounting_date.grid(row=2, sticky="e")
        status = Label(Forms, text="status", font=('arial', 14), bd=15)
        status.grid(row=3, sticky="e")
        amount = Label(Forms, text="amount", font=('arial', 14), bd=15)
        amount.grid(row=4, sticky="e")
        contra_name = Label(Forms, text="contra_name", font=('arial', 14), bd=15)
        contra_name.grid(row=5, sticky="e")
        subject = Label(Forms, text="subject", font=('arial', 14), bd=15)
        subject.grid(row=6, sticky="e")
        comment = Label(Forms, text="comment", font=('arial', 14), bd=15)
        comment.grid(row=7, sticky="e")
        text = Label(Forms, text="text", font=('arial', 14), bd=15)
        text.grid(row=8, sticky="e")

        #==================================FIELDS======================================
        account = Entry(Forms, textvariable=self.account, width=30)
        account.grid(row=0, column=1)
        accounting_no = Entry(Forms, textvariable=self.accounting_no, width=30)
        accounting_no.grid(row=1, column=1)
        accounting_date = Entry(Forms, textvariable=self.accounting_date, width=30)
        accounting_date.grid(row=2, column=1)
        status = Entry(Forms, textvariable=self.status, width=30)
        status.grid(row=3, column=1)
        amount = Entry(Forms, textvariable=self.amount, width=30)
        amount.grid(row=4, column=1)
        contra_name = Entry(Forms, textvariable=self.contra_name, width=30)
        contra_name.grid(row=5, column=1)
        subject = Entry(Forms, textvariable=self.subject, width=30)
        subject.grid(row=6, column=1)
        comment = Entry(Forms, textvariable=self.comment, width=30)
        comment.grid(row=7, column=1)
        text = Entry(Forms, textvariable=self.text, width=30)
        text.grid(row=8, column=1)

        #==================================BUTTONS=====================================
        self.btn_update = Button(Buttons, width=10, text="Update", state=DISABLED)
        self.btn_update.pack(side=RIGHT)
        self.btn_create = Button(Buttons, width=10, text="Create")
        self.btn_create.pack(side=RIGHT)

    def get_current_record(self):
        return Record(
            entry_id=str(self.entry_id.get()),
            account=str(self.account.get()),
            accounting_no=str(self.accounting_no.get()),
            accounting_date=str(self.accounting_date.get()),
            status=str(self.status.get()),
            amount=str(self.amount.get()),
            contra_name=str(self.contra_name.get()),
            subject=str(self.subject.get()),
            comment=str(self.comment.get()),
            text=str(self.text.get())
        )

    def fill_form(self, record):
        self.clear_form()
        self.entry_id.set(record.entry_id)
        self.account.set(record.account)
        self.accounting_no.set(record.accounting_no)
        self.accounting_date.set(record.accounting_date)
        self.status.set(record.status)
        self.amount.set(record.amount)
        self.contra_name.set(record.contra_name)
        self.subject.set(record.subject)
        self.comment.set(record.comment)
        self.text.set(record.text)

        self.btn_create.config(state=DISABLED)
        self.btn_update.config(state=NORMAL)

    def clear_form(self):
        self.account.set("")
        self.accounting_no.set("")
        self.accounting_date.set("")
        self.status.set("")
        self.amount.set("")
        self.contra_name.set("")
        self.subject.set("")
        self.comment.set("")
        self.text.set("")

        self.btn_create.config(state=NORMAL)
        self.btn_update.config(state=DISABLED)

    def is_form_valid(self):
        return self.account.get() == "" or self.accounting_no.get() == "" or self.accounting_date.get() == "" or self.status.get() == "" or self.amount.get() == "" or self.contra_name.get() == "" or self.subject.get() == "" or self.comment.get() == "" or self.text.get() == ""

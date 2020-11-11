#import tkinter as Tk
from tkinter import *


class SidePanel():
    def __init__(self, root, Forms, Buttons):
        self.member_id = StringVar()
        self.first_name = StringVar()
        self.last_name = StringVar()

        #==================================LABELS======================================
        txt_firstname = Label(Forms, text="Firstname:", font=('arial', 14), bd=15)
        txt_firstname.grid(row=0, sticky="e")
        txt_lastname = Label(Forms, text="Lastname:", font=('arial', 14), bd=15)
        txt_lastname.grid(row=1, sticky="e")

        #==================================FIELDS======================================
        firstname = Entry(Forms, textvariable=self.first_name, width=30)
        firstname.grid(row=0, column=1)
        lastname = Entry(Forms, textvariable=self.last_name, width=30)
        lastname.grid(row=1, column=1)

        #==================================BUTTONS=====================================
        self.btn_update = Button(Buttons, width=10, text="Update", state=DISABLED)
        self.btn_update.pack(side=RIGHT)
        self.btn_create = Button(Buttons, width=10, text="Create")
        self.btn_create.pack(side=RIGHT)

    def fill_form(self, member):
        self.clear_form()
        self.member_id.set(member.member_id)
        self.first_name.set(member.first_name)
        self.last_name.set(member.last_name)
        self.btn_create.config(state=DISABLED)
        self.btn_update.config(state=NORMAL)

    def clear_form(self):
        self.first_name.set("")
        self.last_name.set("")
        self.btn_create.config(state=NORMAL)
        self.btn_update.config(state=DISABLED)

    def is_form_valid(self):
        return self.first_name.get() == "" or self.last_name.get() == ""

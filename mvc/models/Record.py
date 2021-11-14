class Record:
    def __init__(self, entry_id, account, accounting_no, accounting_date, status, amount, contra_name, subject, comment, text):
        self.entry_id = entry_id
        self.account = account
        self.accounting_no = accounting_no
        self.accounting_date = accounting_date
        self.status = status
        self.amount = amount
        self.contra_name = contra_name
        self.subject = subject
        self.comment = comment
        self.text = text

    def update(self, account, accounting_no, accounting_date, status, amount, contra_name, subject, comment, text):
        self.account = account
        self.accounting_no = accounting_no
        self.accounting_date = accounting_date
        self.status = status
        self.amount = amount
        self.contra_name = contra_name
        self.subject = subject
        self.comment = comment
        self.text = text

    def as_list(self):
        return {
            'entry_id': self.entry_id,
            'account': self.account,
            'accounting_no': self.accounting_no,
            'accounting_date': self.accounting_date,
            'status': self.status,
            'amount': self.amount,
            'contra_name': self.contra_name,
            'subject': self.subject,
            'comment': self.comment,
            'text': self.text
        }

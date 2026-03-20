from datetime import date

def days_remaining(due_date):
    today = date.today()
    return (due_date - today).days
from datetime import date

def auto_priority(due_date):
    today = date.today()
    days_left = (due_date - today).days

    if days_left <= 1:
        return "High"
    elif days_left <= 3:
        return "Medium"
    else:
        return "Low"

def get_priority_color(priority):
    if priority == "High":
        return "red"
    elif priority == "Medium":
        return "orange"
    else:
        return "green"
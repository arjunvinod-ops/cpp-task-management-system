from datetime import date

def validate_title(title):
    if len(title) < 3:
        return "Task title must be at least 3 characters long"
    return None


def validate_due_date(due_date):
    today = date.today()

    if due_date < today:
        return "Due date cannot be in the past"
    return None
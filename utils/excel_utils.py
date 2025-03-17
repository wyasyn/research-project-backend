import pandas as pd
from models.attendance_model import Attendance

def export_attendance():
    records = Attendance.query.all()
    data = [{"user_id": a.user_id, "date": a.date, "status": a.status} for a in records]
    df = pd.DataFrame(data)
    df.to_excel("attendance.xlsx", index=False)
    return "attendance.xlsx"

import logging, os
import azure.functions as func
import pyodbc
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    user_id = req.params.get("userId")
    if not user_id:
        return func.HttpResponse("Missing userId", status_code=400)

    conn = pyodbc.connect(os.getenv("SQL_CONN_STR"))
    cursor = conn.cursor()
    cursor.execute("SELECT SlotStart, SlotEnd, Topic FROM Schedules WHERE UserId = ?", user_id)
    rows = cursor.fetchall()

    schedule = [{"start": str(r.SlotStart), "end": str(r.SlotEnd), "topic": r.Topic} for r in rows]
    return func.HttpResponse(json.dumps(schedule), mimetype="application/json")

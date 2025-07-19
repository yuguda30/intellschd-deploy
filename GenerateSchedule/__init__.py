import logging, os, json, pickle
import azure.functions as func
from azure.storage.blob import BlobClient
import pyodbc
import pandas as pd

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        user_id = body["userId"]
        courses = body["courses"]  # List of {courseName, examDate}
        availability = body["availability"]  # List of available hours

        # Download model from Blob
        blob = BlobClient.from_connection_string(
            conn_str=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
            container_name="models", blob_name="focus_model.pkl"
        )
        with open("/tmp/focus_model.pkl", "wb") as f:
            f.write(blob.download_blob().readall())
        model = pickle.load(open("/tmp/focus_model.pkl", "rb"))

        # Predict focus scores
        df = pd.DataFrame({"hour": availability})
        df["score"] = model.predict(df[["hour"]])
        df = df.sort_values(by="score", ascending=False)

        # Connect to SQL
        conn = pyodbc.connect(os.getenv("SQL_CONN_STR"))
        cursor = conn.cursor()

        # Write schedules
        for i, course in enumerate(courses):
            slot_hour = int(df.iloc[i]["hour"])
            slot_start = f"{course['examDate']} {slot_hour}:00:00"
            slot_end = f"{course['examDate']} {slot_hour+1}:00:00"
            cursor.execute("""
                INSERT INTO Schedules (UserId, SlotStart, SlotEnd, Topic)
                VALUES (?, ?, ?, ?)
            """, user_id, slot_start, slot_end, course["courseName"])
        conn.commit()

        return func.HttpResponse("Schedule generated", status_code=200)

    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse("Error: " + str(e), status_code=500)

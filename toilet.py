from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from datetime import datetime

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

client = MongoClient('mongodb://localhost', 27017)

db = client["real_mini"]
toilet_collection = db["Toilet"]


class EstimateTime(BaseModel):
    estimate: str
    time: float
    quantity: int


class ToiletOpen(BaseModel):
    room: int
    close: int


class ToiletRoom(BaseModel):
    room_number: int
    close: int
    time_in: int


def calculate_estimate(estimate, spend_time):
    time = estimate["time"]
    quantity = estimate["quantity"]
    all_time = time * quantity
    result = (all_time + spend_time) / (quantity + 1)
    return result


@app.get("/toilet/get-info")
def get_status():
    room1 = toilet_collection.find_one({"room_number": 1}, {"_id": 0})
    room2 = toilet_collection.find_one({"room_number": 2}, {"_id": 0})
    room3 = toilet_collection.find_one({"room_number": 3}, {"_id": 0})
    estime = toilet_collection.find_one({"estimate": "estimate"}, {"_id": 0})
    list_room = list()
    result = list()
    list_room.append(room1)
    list_room.append(room2)
    list_room.append(room3)
    for r in list_room:
        if r["close"] == 0:
            roomnumber = r["room_number"]
            status = "ว่าง"
            str_timestart = "-"
            timestart = "-"
            timeusage = "-"
            timewait = "-"
        else:
            roomnumber = r["room_number"]
            status = "ไม่ว่าง"
            timestart = datetime.fromtimestamp(r["time_in"])
            str_timestart = timestart.strftime("%H") + ":" + timestart.strftime("%M")
            timeusage = datetime.now().timestamp() - r["time_in"]
            timeusage = int(timeusage / 60)
            timewait = int(estime["time"])
        ans = {"roomNumber": roomnumber, "status": status, "timeStart": str_timestart, "timeUsage": timeusage,
               "timeWaiting": timewait}
        # print(ans)
        result.append(ans)
    return {
        "result": result
    }


@app.post("/open-close")
def add_toilet_open_close(status: ToiletOpen):
    room = status.room
    query = toilet_collection.find_one({"room_number": room}, {"_id": 0})
    if query is None:
        raise HTTPException(status_code=404, detail={
            "message": f"Error no room number {room}"
        })
    if status.close:
        toilet_collection.update_one({"room_number": room},
                                     {"$set": {"close": 1, "time_in": datetime.now().timestamp()}})
        return {
            "message": f"Now toilet room {room} in use."
        }
    else:
        toilet_collection.update_one({"room_number": room}, {"$set": {"close": 0}})
        delta = datetime.now().timestamp() - query["time_in"]
        estimate = toilet_collection.find_one({"estimate": "estimate"}, {"_id": 0})
        estimate_time = calculate_estimate(estimate, delta)
        quantity = estimate["quantity"] + 1
        toilet_collection.update_one({"estimate": "estimate"}, {"$set": {"time": estimate_time, "quantity": quantity}})
        return {
            "message": f"Congrats now toilet room {room} is free."
        }

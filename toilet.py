from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from datetime import datetime

app = FastAPI()

client = MongoClient('mongodb://localhost', 27017)

db = client["real_mini"]
toilet_collection = db["Toilet"]

es = {
    "estimate": "estimate",
    "time": datetime.now() - datetime.now(),
    "quantity": 0
}


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
    if time == 0:
        result = spend_time
    else:
        all_time = time * quantity
        result = (all_time + spend_time) / (quantity + 1)
    return result


@app.get("/toilet/by-no/{no}")
def get_status(no: int):
    num = no
    query = {"room": num}
    search = toilet_collection.find_one(query, {"_id": 0})
    return {
        "result": search
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
        toilet_collection.update_one({"room_number": room}, {"$set": {"close": 1, "time_in": datetime.now().timestamp()}})
        return {
            "message": f"Now toilet room {room} in use."
        }
    else:
        toilet_collection.update_one({"room_number": room}, {"$set": {"close": 0}})
        delta = datetime.now().timestamp() - query["time_in"]
        estimate_list = toilet_collection.find_one({"estimate": "estimate"}, {"_id": 0})
        estimate_time = calculate_estimate(estimate_list, delta)
        quantity = estimate_list["quantity"] + 1
        toilet_collection.update_one({"estimate": "estimate"}, {"$set": {"time": estimate_time, "quantity": quantity}})
        return {
            "message": f"Congrats now toilet room {room} is free."
        }

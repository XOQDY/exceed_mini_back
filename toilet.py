from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
import datetime

app = FastAPI()

client = MongoClient('mongodb://localhost', 27017)

db = client["real_mini"]
menu_collection = db["Toilet"]


class ToiletRoom(BaseModel):
    room_number: int
    time_in: datetime.time
    time_out: datetime.time

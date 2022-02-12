from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
import datetime


class ToiletRoom(BaseModel):
    room_number: int
    time_in: datetime.time
    time_out: datetime.time

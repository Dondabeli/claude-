from fastapi import FastAPI, APIRouter, Query, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, date, time


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection (MUST use env variables only)
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()

# Create a router with the /api prefix (critical for ingress)
api_router = APIRouter(prefix="/api")


# Helpers for MongoDB serialization as per guidelines

def prepare_for_mongo(data: Dict[str, Any]) -> Dict[str, Any]:
    if data is None:
        return {}
    out = dict(data)
    # Convert datetime/date/time to strings
    if isinstance(out.get('started_at'), datetime):
        out['started_at'] = out['started_at'].astimezone(timezone.utc).isoformat()
    if isinstance(out.get('ended_at'), datetime):
        out['ended_at'] = out['ended_at'].astimezone(timezone.utc).isoformat()
    if isinstance(out.get('created_at'), datetime):
        out['created_at'] = out['created_at'].astimezone(timezone.utc).isoformat()
    # Coerce date/time fields if present
    if isinstance(out.get('date'), date):
        out['date'] = out['date'].isoformat()
    if isinstance(out.get('time'), time):
        out['time'] = out['time'].strftime('%H:%M:%S')
    return out


def parse_from_mongo(item: Dict[str, Any]) -> Dict[str, Any]:
    if item is None:
        return {}
    out = dict(item)
    # Ignore Mongo _id
    if '_id' in out:
        out.pop('_id', None)
    return out


# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatusCheckCreate(BaseModel):
    client_name: str


class TypingSessionCreate(BaseModel):
    user_id: str
    mode: str = Field(description="time|words|freestyle")
    duration_seconds: int
    words_count: int
    wpm: float
    accuracy: float
    consistency: float
    started_at: Optional[str] = None  # ISO string
    ended_at: Optional[str] = None    # ISO string
    raw_typed: Optional[str] = None
    target_text: Optional[str] = None


class TypingSession(TypingSessionCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LeaderboardEntry(BaseModel):
    user_id: str
    wpm: float
    accuracy: float
    mode: str
    created_at: Optional[str] = None


# Routes
@api_router.get("/")
async def root():
    return {"message": "Hello World"}


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_obj = StatusCheck(client_name=input.client_name)
    await db.status_checks.insert_one(prepare_for_mongo(status_obj.model_dump()))
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(length=1000)
    return [StatusCheck(**parse_from_mongo(status_check)) for status_check in status_checks]


@api_router.post("/sessions", response_model=TypingSession)
async def create_session(input: TypingSessionCreate):
    # Basic validation
    if input.wpm < 0 or input.accuracy < 0:
        raise HTTPException(status_code=400, detail="Invalid metrics")

    session = TypingSession(**input.model_dump())
    await db.typing_sessions.insert_one(prepare_for_mongo(session.model_dump()))
    return session


@api_router.get("/sessions", response_model=List[TypingSession])
async def list_sessions(user_id: Optional[str] = Query(default=None)):
    query = {"user_id": user_id} if user_id else {}
    sessions = await db.typing_sessions.find(query).sort("created_at", -1).to_list(length=200)
    return [TypingSession(**parse_from_mongo(s)) for s in sessions]


@api_router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def leaderboard(mode: Optional[str] = Query(default=None), limit: int = Query(default=10, le=50)):
    query = {}
    if mode:
        query["mode"] = mode
    # Top sessions by wpm with decent accuracy
    cursor = db.typing_sessions.find(query, {"user_id": 1, "wpm": 1, "accuracy": 1, "mode": 1, "created_at": 1}).sort("wpm", -1).limit(limit)
    items = await cursor.to_list(length=limit)
    return [LeaderboardEntry(**parse_from_mongo(x)) for x in items]


# Include the router in the main app
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
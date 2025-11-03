from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3

from kairos_core.content.db import list_songs, add_song, delete_song, get_db
from kairos_core.nlu.df_sync import sync_song_entity
from kairos_core.config import get_settings


router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")


@router.get("", response_class=HTMLResponse)
def portal_home(request: Request, db: sqlite3.Connection = Depends(get_db)):
    songs = list_songs(db)
    settings = get_settings()
    nlu_ready = bool(
        settings.dialogflow_project_id and settings.dialogflow_location and settings.dialogflow_agent_id
    )
    return templates.TemplateResponse(
        "portal.html",
        {
            "request": request,
            "songs": songs,
            "nlu_ready": nlu_ready,
            "song_entity": settings.dialogflow_song_entity,
        },
    )


@router.post("/add")
def portal_add(title: str = Form(...), identifier: str = Form(...), db: sqlite3.Connection = Depends(get_db)):
    add_song(db, title=title, identifier=identifier)
    return RedirectResponse(url="/portal", status_code=303)


@router.post("/delete/{song_id}")
def portal_delete(song_id: int, db: sqlite3.Connection = Depends(get_db)):
    delete_song(db, song_id)
    return RedirectResponse(url="/portal", status_code=303)


@router.post("/nlu/sync")
def portal_nlu_sync(db: sqlite3.Connection = Depends(get_db)):
    titles = [row["title"] for row in list_songs(db)]
    try:
        result = sync_song_entity(titles)
        msg = f"Synced {result['count']} titles to entity {result['entity']}"
        url = f"/portal?msg={msg}"
    except Exception as e:
        url = f"/portal?msg=NLU sync failed: {str(e)}"
    return RedirectResponse(url=url, status_code=303)

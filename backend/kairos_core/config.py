from pydantic import BaseModel
import os


class Settings(BaseModel):
    # External services (placeholders; load from env in real integration)
    google_project_id: str | None = None
    dialogflow_project_id: str | None = os.getenv("DIALOGFLOW_PROJECT_ID")
    dialogflow_location: str | None = os.getenv("DIALOGFLOW_LOCATION", "us-central1")
    dialogflow_agent_id: str | None = os.getenv("DIALOGFLOW_AGENT_ID")
    dialogflow_song_entity: str = os.getenv("DIALOGFLOW_SONG_ENTITY", "SongName")
    acrcloud_host: str | None = None
    acrcloud_key: str | None = None
    acrcloud_secret: str | None = None

    # ProPresenter
    propresenter_host: str = os.getenv("PROP_HOST", "127.0.0.1")
    propresenter_port: int = int(os.getenv("PROP_PORT", "53535"))
    propresenter_password: str | None = os.getenv("PROP_PASSWORD")

    # Behavior
    nlu_confidence_threshold: float = float(os.getenv("NLU_THRESHOLD", "0.8"))


def get_settings() -> Settings:
    return Settings()

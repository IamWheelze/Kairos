from __future__ import annotations

from typing import Iterable

from google.cloud import dialogflowcx_v3 as dialogflowcx

from kairos_core.config import get_settings


def _agent_path(settings) -> str:
    return dialogflowcx.AgentsClient.agent_path(
        project=settings.dialogflow_project_id,
        location=settings.dialogflow_location,
        agent=settings.dialogflow_agent_id,
    )


def sync_song_entity(titles: Iterable[str]) -> dict:
    """Replace the Dialogflow CX entity values for the configured Song entity.

    Returns a summary dict. Requires GOOGLE_APPLICATION_CREDENTIALS and Dialogflow vars.
    """
    settings = get_settings()
    if not (settings.dialogflow_project_id and settings.dialogflow_location and settings.dialogflow_agent_id):
        raise RuntimeError("Dialogflow CX settings not configured")

    ent_client = dialogflowcx.EntityTypesClient()

    # Find entity type by display name
    parent = _agent_path(settings)
    target = None
    for et in ent_client.list_entity_types(parent=parent):
        if et.display_name == settings.dialogflow_song_entity:
            target = et
            break
    if target is None:
        raise RuntimeError(f"Entity type '{settings.dialogflow_song_entity}' not found in agent")

    # Build entities: simple value with itself and lowercase as synonym
    entities = []
    unique = set()
    for t in titles:
        v = (t or "").strip()
        if not v or v.lower() in unique:
            continue
        unique.add(v.lower())
        entities.append(
            dialogflowcx.EntityType.Entity(value=v, synonyms=[v, v.lower()])
        )

    updated = dialogflowcx.EntityType(
        name=target.name,
        display_name=target.display_name,
        kind=target.kind,
        entities=entities,
    )

    from google.protobuf import field_mask_pb2

    mask = field_mask_pb2.FieldMask(paths=["entities"])
    _ = ent_client.update_entity_type(entity_type=updated, update_mask=mask)
    return {"entity": settings.dialogflow_song_entity, "count": len(entities)}


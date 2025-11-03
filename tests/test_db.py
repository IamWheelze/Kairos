import sqlite3
from backend.kairos_core.content.db import init_db, get_conn, add_song, list_songs, get_identifier_by_title, delete_song


def test_db_crud(tmp_path, monkeypatch):
    # Override DB path
    monkeypatch.setattr('backend.kairos_core.content.db.DB_PATH', str(tmp_path / 'kairos.db'))
    init_db()
    conn = get_conn()
    add_song(conn, 'Amazing Grace', 'Library/Songs/AmazingGrace')
    add_song(conn, 'Way Maker', 'Library/Songs/WayMaker')
    rows = list(list_songs(conn))
    assert len(rows) == 2
    ident = get_identifier_by_title(conn, 'Amazing Grace')
    assert ident.endswith('AmazingGrace')
    delete_song(conn, rows[0]['id'])
    rows2 = list(list_songs(conn))
    assert len(rows2) == 1


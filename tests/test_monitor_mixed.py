from __future__ import annotations

import asyncio
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock
from downtify.monitor import PlaylistMonitorDB, MonitoredPlaylist


def test_monitor_db_mixed_operations(tmp_path: Path):
    db_path = tmp_path / 'monitor.db'
    db = PlaylistMonitorDB(db_path)

    # 1. Add a playlist
    pl = db.add_playlist(
        spotify_id='playlist_id_123',
        name='My Playlist',
        url='https://open.spotify.com/playlist/playlist_id_123',
        interval_minutes=60,
        type='playlist'
    )
    assert pl.spotify_id == 'playlist_id_123'
    assert pl.name == 'My Playlist'
    assert pl.type == 'playlist'

    # 2. Add an artist
    art = db.add_playlist(
        spotify_id='artist_id_456',
        name='HOYO-MiX',
        url='https://open.spotify.com/artist/artist_id_456',
        interval_minutes=180,
        type='artist'
    )
    assert art.spotify_id == 'artist_id_456'
    assert art.name == 'HOYO-MiX'
    assert art.type == 'artist'

    # 3. List playlists
    items = db.list_playlists()
    assert len(items) == 2
    types = {item.type for item in items}
    assert types == {'playlist', 'artist'}

    # 4. Get by spotify_id
    retrieved_art = db.get_by_spotify_id('artist_id_456')
    assert retrieved_art is not None
    assert retrieved_art.type == 'artist'
    assert retrieved_art.name == 'HOYO-MiX'

    # 5. Mark release downloaded
    releases = db.get_downloaded_releases(art.id)
    assert len(releases) == 0

    db.mark_release_downloaded(art.id, 'release_aaa')
    db.mark_release_downloaded(art.id, 'release_bbb')

    releases_after = db.get_downloaded_releases(art.id)
    assert releases_after == {'release_aaa', 'release_bbb'}

    # 6. Delete playlist and check cascade
    db.delete_playlist(art.id)
    items_after = db.list_playlists()
    assert len(items_after) == 1
    assert items_after[0].type == 'playlist'


@patch('downtify.spotify.artist_releases_from_id')
@patch('downtify.spotify.album_tracks_from_id')
def test_check_artist_flow(mock_album_tracks, mock_releases, tmp_path):
    db_path = tmp_path / 'monitor.db'
    db = PlaylistMonitorDB(db_path)
    art = db.add_playlist(
        spotify_id='artist_id_456',
        name='HOYO-MiX',
        url='https://open.spotify.com/artist/artist_id_456',
        interval_minutes=180,
        type='artist'
    )

    mock_releases.side_effect = lambda sid, rtype: ['rel_1'] if rtype == 'album' else []
    mock_album_tracks.return_value = [{'song_id': 'track_1', 'name': 'Track 1', 'artists': ['HOYO-MiX']}]

    mock_downloader = MagicMock()
    mock_downloader.download_dir = tmp_path
    mock_downloader.download.return_value = 'HOYO-MiX - Track 1.mp3'

    broadcast = MagicMock()
    loop = asyncio.get_event_loop_policy().get_event_loop()

    from downtify.monitor import check_artist
    downloaded = loop.run_until_complete(
        check_artist(art, db, mock_downloader, broadcast, loop)
    )

    assert downloaded == 1
    releases = db.get_downloaded_releases(art.id)
    assert releases == {'rel_1'}


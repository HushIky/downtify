from __future__ import annotations

from unittest.mock import patch, MagicMock
import pytest
from downtify import spotify

def test_artist_info_from_id_success():
    mock_gql_payload = {
        'data': {
            'artistUnion': {
                'profile': {
                    'name': 'HOYO-MiX'
                },
                'uri': 'spotify:artist:2YvlK6lKiKVjXxsjvNbnqg'
            }
        }
    }
    
    def mock_get(url, *args, **kwargs):
        resp = MagicMock()
        resp.status_code = 200
        if 'embed' in url:
            resp.text = '<html><script id="__NEXT_DATA__" type="application/json">{"props":{"pageProps":{"state":{"settings":{"session":{"accessToken":"dummy"}}}}}}</script></html>'
        else:
            resp.json.return_value = mock_gql_payload
        resp.raise_for_status = lambda: None
        return resp

    with patch('downtify.spotify.requests.get', side_effect=mock_get):
        res = spotify.artist_info_from_id('2YvlK6lKiKVjXxsjvNbnqg')
        assert res['name'] == 'HOYO-MiX'
        assert res['id'] == '2YvlK6lKiKVjXxsjvNbnqg'
        assert res['uri'] == 'spotify:artist:2YvlK6lKiKVjXxsjvNbnqg'


def test_artist_releases_from_id_success():
    mock_gql_payload = {
        'data': {
            'artistUnion': {
                'discography': {
                    'albums': {
                        'items': [
                            {
                                'releases': {
                                    'items': [
                                        {'id': 'album_1'}
                                    ]
                                }
                            }
                        ],
                        'totalCount': 1
                    }
                }
            }
        }
    }

    def mock_get(url, *args, **kwargs):
        resp = MagicMock()
        resp.status_code = 200
        if 'embed' in url:
            resp.text = '<html><script id="__NEXT_DATA__" type="application/json">{"props":{"pageProps":{"state":{"settings":{"session":{"accessToken":"dummy"}}}}}}</script></html>'
        else:
            resp.json.return_value = mock_gql_payload
        resp.raise_for_status = lambda: None
        return resp

    with patch('downtify.spotify.requests.get', side_effect=mock_get):
        res = spotify.artist_releases_from_id('2YvlK6lKiKVjXxsjvNbnqg', 'album')
        assert res == ['album_1']

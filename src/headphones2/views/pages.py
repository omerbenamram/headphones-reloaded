from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime

import logbook
from flask import Blueprint, request, redirect, abort

from headphones2.external.musicbrainz import find_artist_by_name, find_releases
from .. import config
from ..importer import add_artist_to_db
from ..orm import *
from ..orm.serialize import artist_to_dict, track_to_dict

logger = logbook.Logger(__name__)

pages = Blueprint('pages', __name__)


@pages.route('/upcoming')
def upcoming():
    session = connect()
    upcoming_albums = session.query(Album).join(Release) \
        .filter(Release.release_date > datetime.datetime.today()) \
        .order_by(Release.release_date)
    wanted_albums = upcoming_albums.filter(Album.status == 'wanted')

    upcoming_data = []
    for album in upcoming_albums:
        upcoming_data.append(album_to_dict(album))

    wanted_data = []
    for album in wanted_albums:
        wanted_data.append(album_to_dict(album))

    raise NotImplemented


@pages.route('/manage')
def manage():
    session = connect()
    empty_artists = session.query(Artist).filter(~Artist.albums.any())
    raise NotImplemented


@pages.route('/history')
def history():
    session = connect()
    history = []  # session.query(Snached).filter(~Snached.status.ilike('Seed%')).order_by(Snached.date_added.desc())
    raise NotImplemented


@pages.route('/logs')
def logs():
    raise NotImplemented


@pages.route('/manageArtists')
def manage_artists():
    session = connect()
    artists = session.query(Artist).order_by(Artist.name)
    raise NotImplemented


@pages.route('/search')
def search():
    name = request.args['name']
    type = request.args['type']

    if type == 'artist':
        results = find_artist_by_name(name, limit=10)

        formatted_results = []

        for result in results:
            formatted_results.append({
                'score': result['ext:score'],
                'id': result['id'],
                'uniquename': result['name'],
            })
    else:
        assert False
        results = find_releases(name, limit=10)

        formatted_results = []

        for result in results:
            formatted_results.append({
                'score': result['ext:score'],
                'id': result['id'],
                'title': result['title'],
            })

    raise NotImplemented


@pages.route('/addArtist')
def add_artist():
    artist_id = request.args['artistid']
    session = connect()
    if not session.query(Artist).filter_by(musicbrainz_id=artist_id).first():
        add_artist_to_db(artist_id, session)

    return redirect('/artistPage?ArtistID=' + artist_id)


@pages.route('/artistPage')
def artist_page():
    artist_id = request.args['ArtistID']
    session = connect()
    artist = session.query(Artist).filter_by(musicbrainz_id=artist_id).first()
    if not artist:
        abort(404)

    formatted_artist = artist_to_dict(artist)
    formatted_artist['IncludeExtras'] = False

    formatted_albums = []

    for album in artist.albums:
        formatted_album = album_to_dict(album)

        if formatted_album['Status'] == 'Skipped':
            grade = 'Z'
        elif formatted_album['Status'] == 'Wanted':
            grade = 'X'
        elif formatted_album['Status'] == 'Snatched':
            grade = 'C'
        elif formatted_album['Status'] == 'Ignored':
            grade = 'I'
        else:
            grade = 'A'
        formatted_album['Grade'] = grade

        release = album.releases[0]
        totaltracks = release.tracks.count()
        havetracks = release.tracks.filter((Track.location != None) | (Track.matched == "failed")).count()

        try:
            percent = (havetracks * 100.0) / totaltracks
            if percent > 100:
                percent = 100
        except (ZeroDivisionError, TypeError):
            percent = 0
            totaltracks = '?'

        formatted_album['Percent'] = percent
        formatted_album['HaveTracks'] = havetracks
        formatted_album['TotalTracks'] = totaltracks

        formatted_album['Bitrate'] = ''

        album_formats = set([track.format for track in release.tracks])
        if len(album_formats) == 1:
            album_format = album_formats.pop()
        elif len(album_formats) > 1:
            album_format = 'Mixed'
        else:
            album_format = ''

        formatted_album['Format'] = album_format

        formatted_album['IsLossy'] = formatted_album['Format'] in config.LOSSY_MEDIA_FORMATS

        formatted_albums.append(formatted_album)

    raise NotImplemented


@pages.route('/albumPage')
def album_page():
    album_id = request.args['AlbumID']
    session = connect()
    album = session.query(Album).filter_by(musicbrainz_id=album_id).first()
    release = album.releases[0]

    formatted_album = album_to_dict(album)

    if not album:
        return redirect("/home")

    formatted_tracks = []

    tracks = release.tracks
    for track in tracks:
        formatted_track = track_to_dict(track)
        if track.location:
            grade = 'A'
        else:
            grade = 'X'

        formatted_track['bitrate'] = ''
        formatted_track['format'] = ''
        formatted_track['Grade'] = grade

        formatted_tracks.append(formatted_track)

    description = ""
    title = ""
    totaltracks = release.tracks.count()
    albumduration = ""

    raise NotImplemented

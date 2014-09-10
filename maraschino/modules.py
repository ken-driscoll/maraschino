# -*- coding: utf-8 -*-
"""This file contains the descriptions and settings for all modules. Also it contains functions to add modules and so on"""

try:
    import json
except ImportError:
    import simplejson as json

from flask import jsonify, render_template, request
from maraschino.database import db_session

import maraschino
import copy

from Maraschino import app
from maraschino.tools import *

from maraschino.database import *
from maraschino.models import Module, NewznabSite

# name, label, description, and static are not user-editable and are taken from here
# poll and delay are user-editable and saved in the database - the values here are the defaults
# settings are also taken from the database - the values here are defaults
# if static = True then poll and delay are ignored

AVAILABLE_MODULES = [
    {
        'name': 'couchpotato',
        'label': 'Manager - CouchPotato',
        'description': 'Manage CouchPotato from within Maraschino',
        'static': True,
        'poll': 0,
        'delay': 0,
        'settings': [
            {
                'key': 'couchpotato_api',
                'value': '',
                'description': 'CouchPotato API Key',
            },
            {
                'key': 'couchpotato_user',
                'value': '',
                'description': 'CouchPotato Username',
            },
            {
                'key': 'couchpotato_password',
                'value': '',
                'description': 'CouchPotato Password',
            },
            {
                'key': 'couchpotato_ip',
                'value': '',
                'description': 'CouchPotato Hostname',
            },
            {
                'key': 'couchpotato_port',
                'value': '',
                'description': 'CouchPotato Port',
            },
            {
                'key': 'couchpotato_webroot',
                'value': '',
                'description': 'CouchPotato Webroot',
            },
            {
                'key': 'couchpotato_https',
                'value': '0',
                'description': 'Use HTTPS',
                'type': 'bool',
            },
            {
                'key': 'couchpotato_compact',
                'value': '0',
                'description': 'Compact view',
                'type': 'bool',
            },
        ]
    },
    {
        'name': 'headphones',
        'label': 'Manager - Headphones',
        'description': 'Manage Headphones from within Maraschino',
        'static': True,
        'poll': 0,
        'delay': 0,
        'settings': [
            {
                'key': 'headphones_host',
                'value': '',
                'description': 'Headphones Hostname',
            },
            {
                'key': 'headphones_port',
                'value': '',
                'description': 'Headphones Port',
            },
            {
                'key': 'headphones_webroot',
                'value': '',
                'description': 'Headphones Webroot',
            },
            {
                'key': 'headphones_user',
                'value': '',
                'description': 'Headphones Username',
            },
            {
                'key': 'headphones_password',
                'value': '',
                'description': 'Headphones Password',
            },
            {
                'key': 'headphones_api',
                'value': '',
                'description': 'Headphones API Key',
            },
            {
                'key': 'headphones_https',
                'value': '0',
                'description': 'Use HTTPS',
                'type': 'bool',
            },
            {
                'key': 'headphones_compact',
                'value': '0',
                'description': 'Compact view',
                'type': 'bool',
            },
        ]
    },
    {
        'name': 'sickbeard',
        'label': 'Manager - Sickbeard',
        'description': 'Manage Sickbeard from within Maraschino',
        'static': True,
        'poll': 0,
        'delay': 0,
        'settings': [
            {
                'key': 'sickbeard_api',
                'value': '',
                'description': 'Sickbeard API Key',
            },
            {
                'key': 'sickbeard_user',
                'value': '',
                'description': 'Sickbeard Username',
            },
            {
                'key': 'sickbeard_password',
                'value': '',
                'description': 'Sickbeard Password',
            },
            {
                'key': 'sickbeard_ip',
                'value': '',
                'description': 'Sickbeard Hostname',
            },
            {
                'key': 'sickbeard_port',
                'value': '',
                'description': 'Sickbeard Port',
            },
            {
                'key': 'sickbeard_webroot',
                'value': '',
                'description': 'Sickbeard Webroot',
            },
            {
                'key': 'sickbeard_https',
                'value': '0',
                'description': 'Use HTTPS',
                'type': 'bool',
            },
            {
                'key': 'sickbeard_compact',
                'value': '0',
                'description': 'Compact view',
                'type': 'bool',
            },
            {
                'key': 'sickbeard_airdate',
                'value': '0',
                'description': 'Show air date',
                'type': 'bool',
            },
        ]
    },
    {
        'name': 'nzbdrone',
        'label': 'Manager - NZBDrone',
        'description': 'Manage NZBDrone from within Maraschino',
        'static': True,
        'poll': 0,
        'delay': 0,
        'settings': [
            {
                'key': 'nzbdrone_api',
                'value': '',
                'description': 'nzbdrone API Key',
            },
            {
                'key': 'nzbdrone_ip',
                'value': '',
                'description': 'nzbdrone Hostname',
            },
            {
                'key': 'nzbdrone_port',
                'value': '',
                'description': 'nzbdrone Port',
            },
            {
                'key': 'nzbdrone_webroot',
                'value': '',
                'description': 'nzbdrone Webroot',
            },
            {
                'key': 'nzbdrone_https',
                'value': '0',
                'description': 'Use HTTPS',
                'type': 'bool',
            },
            {
                'key': 'nzbdrone_compact',
                'value': '0',
                'description': 'Compact view',
                'type': 'bool',
            },
            {
                'key': 'nzbdrone_airdate',
                'value': '0',
                'description': 'Show air date',
                'type': 'bool',
            },
        ]
    },
    {
        'name': 'plex',
        'label': 'Plex Module',
        'description': 'Check your Plex Server content - OnDeck and Library',
        'static': True,
        'poll': 0,
        'delay': 0,
    },
    {
        'name': 'plex_recent_movies',
        'label': 'Plex - Recently Added Movies',
        'description': 'See the latest Movies from your Plex Library',
        'static': False,
        'poll': 360,
        'delay': 0,
    },
    {
        'name': 'plex_recent_episodes',
        'label': 'Plex - Recently Added Episodes',
        'description': 'See the latest Episodes from your Plex Library',
        'static': False,
        'poll': 360,
        'delay': 0,
    },
    {
        'name': 'plex_recent_albums',
        'label': 'Plex - Recently Added Albums',
        'description': 'See the latest Albums from your Plex Library',
        'static': False,
        'poll': 360,
        'delay': 0,
    },
    {
        'name': 'plex_recent_photos',
        'label': 'Plex - Recently Added Photos',
        'description': 'See the latest Photos from your Plex Library',
        'static': False,
        'poll': 360,
        'delay': 0,
    },
    {
        'name': 'nzbget',
        'label': 'Usenet - NZBGet',
        'description': 'Shows you information about your NZBGet downloads.',
        'static': False,
        'poll': 10,
        'delay': 0,
        'settings': [
            {
                'key': 'nzbget_host',
                'value': '',
                'description': 'Hostname',
            },
            {
                'key': 'nzbget_port',
                'value': '',
                'description': 'Port',
            },
            {
                'key': 'nzbget_username',
                'value': '',
                'description': 'Username',
            },
            {
                'key': 'nzbget_password',
                'value': '',
                'description': 'Password',
            },
            {
                'key': 'nzbget_https',
                'value': '0',
                'description': 'Use HTTPS',
                'type': 'bool',
            },
        ]
    },
    {
        'name': 'sabnzbd',
        'label': 'Usenet - SABnzbd+',
        'description': 'Shows you information about your SABnzbd+ downloads.',
        'static': False,
        'poll': 10,
        'delay': 0,
        'settings': [
            {
                'key': 'sabnzbd_host',
                'value': '',
                'description': 'Hostname',
            },
            {
                'key': 'sabnzbd_port',
                'value': '',
                'description': 'Port',
            },
            {
                'key': 'sabnzbd_webroot',
                'value': '',
                'description': 'Webroot',
            },
            {
                'key': 'sabnzbd_api',
                'value': '',
                'description': 'API Key',
            },
            {
                'key': 'sabnzbd_https',
                'value': '0',
                'description': 'Use HTTPS',
                'type': 'bool',
            },
            {
                'key': 'sabnzbd_show_empty',
                'value': '1',
                'description': 'Show module when queue is empty',
                'type': 'bool',
            },
        ]
    },
    {
        'name': 'transmission',
        'label': 'Torrent - Transmission',
        'description': 'Shows you information about your Transmission downloads.',
        'static': False,
        'poll': 10,
        'delay': 0,
        'settings': [
                {
                'key': 'transmission_ip',
                'value': '',
                'description': 'Transmission Hostname',
                },
                {
                'key': 'transmission_port',
                'value': '9091',
                'description': 'Transmission Port',
                },
                {
                'key': 'transmission_user',
                'value': '',
                'description': 'Transmission Username',
                },
                {
                'key': 'transmission_password',
                'value': '',
                'description': 'Transmission Password',
                },
                {
                    'key': 'transmission_webroot',
                    'value': '',
                    'description': 'Transmission Webroot (Optional)',
                },
                {
                'key': 'transmission_show_empty',
                'value': '1',
                'description': 'Show module with no active torrents',
                'type': 'bool',
                },
        ]
    },
    {
        'name': 'utorrent',
        'label': 'Torrent - uTorrent',
        'description': 'Shows information about uTorrent downloads',
        'static': False,
        'poll': 10,
        'delay': 0,
        'settings': [
                {
                'key': 'utorrent_ip',
                'value': '',
                'description': 'uTorrent Hostname',
                },
                {
                'key': 'utorrent_port',
                'value': '8080',
                'description': 'uTorrent Port',
                },
                {
                'key': 'utorrent_user',
                'value': '',
                'description': 'uTorrent Username',
                },
                {
                'key': 'utorrent_password',
                'value': '',
                'description': 'uTorrent Password',
                },
        ]
    },
    {
        'name': 'traktplus',
        'label': 'Trakt.TV',
        'description': 'trakt.tv module',
        'static': False,
        'poll': 0,
        'delay': 10,
        'settings': [
            {
                'key': 'trakt_api_key',
                'value': '',
                'description': 'Trakt API Key',
                'link': 'http://trakt.tv/settings/api',
            },
            {
                'key': 'trakt_username',
                'value': '',
                'description': 'Trakt Username',
            },
            {
                'key': 'trakt_password',
                'value': '',
                'description': 'Trakt Password',
            },
            {
                'key': 'trakt_default_view',
                'value': 'trending',
                'description': 'Default view',
                'type': 'select',
                'options': [
                    {'value': 'trending_shows', 'label': 'Trending (TV Shows)'},
                    {'value': 'trending_movies', 'label': 'Trending (Movies)'},
                    {'value': 'activity_friends', 'label': 'Activity (Friends)'},
                    {'value': 'activity_community', 'label': 'Activity (Community)'},
                    {'value': 'friends', 'label': 'Friends'},
                    {'value': 'calendar' , 'label': 'Calendar'},
                    {'value': 'recommendations_shows' , 'label': 'Recommendations (TV Shows)'},
                    {'value': 'recommendations_movies' , 'label': 'Recommendations (Movies)'},
                    {'value': 'profile' , 'label': 'My profile'},
                ]
            },
            {
                'key': 'trakt_default_media',
                'value': 'shows',
                'description': 'Default media type',
                'type': 'select',
                'options': [
                    {'value': 'shows', 'label': 'Shows'},
                    {'value': 'movies', 'label': 'Movies'},
                ]
            },
            {
                'key': 'trakt_trending_limit',
                'value': '20',
                'description': 'How many trending items to display',
                'type': 'select',
                'options': [
                    {'value': '20', 'label': '20'},
                    {'value': '40', 'label': '40'},
                    {'value': '60', 'label': '60'},
                ]
            },
        ]
    },
    {
        'name': 'trakt',
        'label': 'Trakt.TV - Shouts',
        'description': 'Shows you what people are saying about what you are watching and allows you to add your own comments.',
        'static': True,
        'poll': 0,
        'delay': 0,
        'settings': [
            {
                'key': 'trakt_api_key',
                'value': '',
                'description': 'Trakt API Key',
                'link': 'http://trakt.tv/settings/api',
            },
            {
                'key': 'trakt_username',
                'value': '',
                'description': 'Trakt Username',
            },
            {
                'key': 'trakt_password',
                'value': '',
                'description': 'Trakt Password',
            },
        ]
    },
    {
        'name': 'applications',
        'label': 'Utility - Applications',
        'description': 'Allows you to link to whatever applications you want (SabNZBd, SickBeard, etc.)',
        'static': True,
        'poll': 0,
        'delay': 0,
        'settings': [
            {
                'key': 'app_new_tab',
                'value': '0',
                'description': 'Open application in new tab.',
                'type': 'bool',
            },
        ]
    },
    {
        'name': 'diskspace',
        'label': 'Utility - Disk space',
        'description': 'Shows you available disk space on your various drives.',
        'static': False,
        'poll': 350,
        'delay': 0,
        'settings': [
            {
                'key': 'show_grouped_disks',
                'value': '0',
                'description': 'Show grouped disks outside of group.',
                'type': 'bool',
            },
            {
                'key': 'use_binary_units',
                'value': '1',
                'description': 'Use binary storage units (eg. GiB rather than GB)',
                'type': 'bool',
            },
        ]
    },
    {
        'name':'ipcamera',
        'label':'Utility - IP Camera',
        'description':'Show and control your ip camera',
        'static': False,
        'poll': 0,
        'delay': 0,
        'settings': [
                {
                'key': 'ipcamera_ip',
                'value': '',
                'description': 'Ip',
                },
                {
                'key': 'ipcamera_port',
                'value': '',
                'description': 'Port',
                },
                {
                'key': 'ipcamera_username',
                'value': '',
                'description': 'Username',
                },
                {
                'key': 'ipcamera_password',
                'value': '',
                'description': 'Password',
                },
                {
                'key': 'ipcamera_type',
                'value': 'fosscammjeg',
                'description': 'Pick your camera',
                'type': 'select',
                'options': [
                    {'value':'foscammjeg', 'label':'Foscam MJEG'},
                    {'value':'foscammp4', 'label':'Foscam MP4'},
                ]
            },
        ]
    },
    {
        'name': 'script_launcher',
        'label': 'Utility - Script Launcher',
        'description': 'Runs scripts on same system Maraschino is located.',
        'static': False,
        'poll': 350,
        'delay': 0,
    },
    {
        'name': 'weather',
        'label': 'Utility - Weather',
        'description': 'Weather details.',
        'static': False,
        'poll': 350,
        'delay': 0,
        'settings': [
            {
                'key': 'weather_location',
                'value': '',
                'description': 'weather.com area ID',
                'link': 'http://edg3.co.uk/snippets/weather-location-codes/',
            },
            {
                'key': 'weather_use_celcius',
                'value': '0',
                'description': 'Temperature in C',
                'type': 'bool',
            },
            {
                'key': 'weather_use_kilometers',
                'value': '0',
                'description': 'Wind Speed in Km',
                'type': 'bool',
            },
            {
                'key': 'weather_time',
                'value': '0',
                'description': '24 hour time',
                'type': 'bool',
            },
            {
                'key': 'weather_compact',
                'value': '0',
                'description': 'Compact view',
                'type': 'bool',
            },
        ]
    },
]

MISC_SETTINGS = [
    {
        'key': 'random_backgrounds',
        'value': '0',
        'description': 'Use a random background when not watching media',
        'type': 'bool',
    },
    {
        'key': 'num_columns',
        'value': '3',
        'description': 'Number of columns',
        'type': 'select',
        'options': [
            {'value': '3', 'label': '3'},
            {'value': '4', 'label': '4'},
            {'value': '5', 'label': '5'},
        ]
    },
    {
        'key': 'title_color',
        'value': 'EEE',
        'description': 'Module title color (hexadecimal)',
    },
]

SERVER_SETTINGS = [
    {
        'key': 'maraschino_username',
        'value': '',
        'description': 'Maraschino username',
    },
    {
        'key': 'maraschino_password',
        'value': '',
        'description': 'Maraschino password',
    },
    {
        'key': 'maraschino_port',
        'value': '7000',
        'description': 'Maraschino port',
    },
    {
        'key': 'maraschino_webroot',
        'value': '',
        'description': 'Maraschino webroot',
    },
]

SEARCH_SETTINGS = [
    {
        'key': 'search',
        'value': '0',
        'description': 'Enable search feature',
        'type': 'bool',
    },
    {
        'key': 'search_retention',
        'value': '',
        'description': 'Usenet retention',
    },
    {
        'key': 'search_ssl',
        'value': '0',
        'description': 'Prefer SSL',
        'type': 'bool',
    },
    {
        'key': 'search_english',
        'value': '0',
        'description': 'Prefer English only',
        'type': 'bool',
    },
]


PLEX = [
    {
        'key': 'myPlex_username',
        'value': '',
        'description': 'myPlex username',
    },
    {
        'key': 'myPlex_password',
        'value': '',
        'description': 'myPlex password',
    },
]


@app.route('/xhr/add_module_dialog')
@requires_auth
def add_module_dialog():
    """Dialog to add a new module to Maraschino"""
    modules_on_page = Module.query.all()
    available_modules = copy.copy(AVAILABLE_MODULES)

    # filter all available modules that are not currently on the page
    for module_on_page in modules_on_page:
        for available_module in available_modules:
            if module_on_page.name == available_module['name']:
                available_modules.remove(available_module)
                break

    return render_template('dialogs/add_module_dialog.html',
        available_modules = available_modules,
    )

@app.route('/xhr/add_module', methods=['POST'])
@requires_auth
def add_module():
    """Add a new module to Maraschino"""
    try:
        module_id = request.form['module_id']
        column = request.form['column']
        position = request.form['position']

        # make sure that it's a valid module

        module_info = get_module_info(module_id)

        if not module_info:
            raise Exception

    except:
        return jsonify({ 'status': 'error' })

    module = Module(
        module_info['name'],
        column,
        position,
        module_info['poll'],
        module_info['delay'],
    )

    db_session.add(module)

    # if module template has extra settings then create them in the database
    # with default values if they don't already exist

    if 'settings' in module_info:
        for s in module_info['settings']:
            setting = get_setting(s['key'])

            if not setting:
                setting = Setting(s['key'], s['value'])
                db_session.add(setting)

    db_session.commit()

    module_info['template'] = '%s.html' % (module_info['name'])

    # if the module is static and doesn't have any extra settings, return
    # the rendered module

    if module_info['static'] and not 'settings' in module_info:
        return render_template('placeholder_template.html',
            module = module_info
        )

    # otherwise return the rendered module settings dialog

    else:
        return module_settings_dialog(module_info['name'])

@app.route('/xhr/rearrange_modules', methods=['POST'])
@requires_auth
def rearrange_modules():
    """Rearrange a module on the page"""
    try:
        modules = json.JSONDecoder().decode(request.form['modules'])
    except:
        return jsonify({ 'status': 'error' })

    for module in modules:
        try:
            m = Module.query.filter(Module.name == module['name']).first()
            m.column = module['column']
            m.position = module['position']
            db_session.add(m)
        except:
            pass

    db_session.commit()

    return jsonify({ 'status': 'success' })

@app.route('/xhr/remove_module/<name>', methods=['POST'])
@requires_auth
def remove_module(name):
    """Remove module from the page"""
    module = Module.query.filter(Module.name == name).first()
    db_session.delete(module)
    db_session.commit()

    return jsonify({ 'status': 'success' })

@app.route('/xhr/module_settings_dialog/<name>')
@requires_auth
def module_settings_dialog(name):
    """show settings dialog for module"""
    module_info = get_module_info(name)
    module_db = get_module(name)

    if module_info and module_db:

        # look at the module template so we know what settings to look up

        module = copy.copy(module_info)

        # look up poll and delay from the database

        module['poll'] = module_db.poll
        module['delay'] = module_db.delay

        # iterate through possible settings and get values from database

        if 'settings' in module:
            for s in module['settings']:
                setting = get_setting(s['key'])

                if setting:
                    s['value'] = setting.value

                if 'plex_servers' in s:
                    s['options'] = module_get_plex_servers()

        return render_template('dialogs/module_settings_dialog.html',
            module = module,
        )

    return jsonify({ 'status': 'error' })

@app.route('/xhr/module_settings_cancel/<name>')
@requires_auth
def module_settings_cancel(name):
    """Cancel the settings dialog"""
    module = get_module_info(name)

    if module:
        module['template'] = '%s.html' % (module['name'])

        return render_template('placeholder_template.html',
            module = module,
        )

    return jsonify({ 'status': 'error' })

@app.route('/xhr/module_settings_save/<name>', methods=['POST'])
@requires_auth
def module_settings_save(name):
    """Save options in settings dialog"""
    try:
        settings = json.JSONDecoder().decode(request.form['settings'])
    except:
        return jsonify({ 'status': 'error' })

    for s in settings:

        # poll and delay are stored in the modules tables

        if s['name'] == 'poll' or s['name'] == 'delay':
            module = get_module(name)

            if s['name'] == 'poll':
                module.poll = int(s['value'])

            if s['name'] == 'delay':
                module.delay = int(s['value'])

            db_session.add(module)

        # other settings are stored in the settings table

        else:
            setting = get_setting(s['name'])

            if not setting:
                setting = Setting(s['name'])

            setting.value = s['value']
            db_session.add(setting)

            if s['name'] == 'maraschino_username':
                maraschino.AUTH['username'] = s['value'] if s['value'] != '' else None

            if s['name'] == 'maraschino_password':
                maraschino.AUTH['password'] = s['value'] if s['value'] != '' else None

    db_session.commit()

    # you can't cancel server settings - instead, return an updated template
    # with 'Settings saved' text on the button

    if name == 'server_settings':
        return extra_settings_dialog(dialog_type='server_settings', updated=True)
    elif name == 'plex_login':
        from maraschino.noneditable import json_login
        try:
            return json_login()
        except:
            logger.log('Plex :: Failed to populate servers with new credentials', 'ERROR')


    # for everything else, return the rendered module

    return module_settings_cancel(name)

@app.route('/xhr/extra_settings_dialog/<dialog_type>')
@requires_auth
def extra_settings_dialog(dialog_type, updated=False):
    """
    Extra settings dialog (search settings, misc settings, etc).
    """

    dialog_text = None
    dialog_extra = None

    if dialog_type == 'search_settings':
        settings = copy.copy(SEARCH_SETTINGS)
        dialog_title = 'Search settings'
        dialog_text = 'N.B. With search enabled, you can press \'ALT-s\' to display the search module.'
        dialog_extra = NewznabSite.query.order_by(NewznabSite.id)

    elif dialog_type == 'misc_settings':
        settings = copy.copy(MISC_SETTINGS)
        dialog_title = 'Misc. settings'

    elif dialog_type == 'server_settings':
        settings = copy.copy(SERVER_SETTINGS)
        dialog_title = 'Server settings'

    elif dialog_type == 'plex_login':
        settings = copy.copy(PLEX)
        dialog_text = 'Credentials to log into http://plex.tv.'
        dialog_title = 'myPlex Credentials'

    else:
        return jsonify({ 'status': 'error' })

    for s in settings:
        setting = get_setting(s['key'])

        if setting:
            s['value'] = setting.value

    return render_template('dialogs/extra_settings_dialog.html',
        dialog_title=dialog_title,
        dialog_text=dialog_text,
        dialog_type=dialog_type,
        dialog_extra=dialog_extra,
        settings=settings,
        updated=updated,
    )

def get_module(name):
    """helper method which returns a module record from the database"""
    try:
        return Module.query.filter(Module.name == name).first()

    except:
        return None

def get_module_info(name):
    """helper method which returns a module template"""
    for available_module in AVAILABLE_MODULES:
        if name == available_module['name']:
            return available_module

    return None

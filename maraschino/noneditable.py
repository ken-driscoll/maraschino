# -*- coding: utf-8 -*-
"""Util funtions for Plex server settings."""

from maraschino.tools import get_setting_value, get_setting, requires_auth
from maraschino.models import PlexServer, Setting
from maraschino.database import db_session
from plexLib import Server, User
from maraschino import logger, app
from flask import jsonify, request
try:
    import json
except ImportError:
    import simplejson as json

user = None
servers = None

@app.route('/xhr/plex/tutorial_save/', methods=['POST'])
def tutorial_save():
    global user, servers
    # save login and password on db
    try:
        settings = json.JSONDecoder().decode(request.form['settings'])
        for s in settings:
            setting = get_setting(s['name'])

            if not setting:
                setting = Setting(s['name'])

            setting.value = s['value']
            db_session.add(setting)
        db_session.commit()
        logger.log('Plex :: Successfully saved Plex credentials', 'INFO')
    except:
        return jsonify(success=False, msg='Failed to save plex credentials to db')

    # Delete info for previous accounts
    try:
        PlexServer.query.delete()
    except:
        logger.log('Plex :: Failed to delete old server info', 'WARNING')

    try:
        if loginToPlex(): # login to plex
            servers = getServers()
            if servers: # retrieve servers
                return jsonify(success=True, servers=listServers())
            else:
                return jsonify(sucess=False, msg='Failed to retrieve servers')
        else:
            return jsonify(sucess=False, msg='Failed to login to plex')
    except:
        return jsonify(success=False, msg='Servers not populated Successfully')


@app.route('/xhr/plex/login/')
@requires_auth
def json_login():
    if not loginToPlex():
        return jsonify(success=False, msg='Failed to login to plex.tv, plese make sure this is a valid username/password.')

    # Delete info for previous accounts
    try:
        PlexServer.query.delete()
    except:
        logger.log('Plex :: Failed to delete old server info', 'WARNING')

    # Populate servers for new user
    if not getServers():
        return jsonify(success=False, msg='Failed to retrieve server information from https://plex.tv/pms/servers.')

    # Set active server to 0 (no server selected)
    try:
        active_server = get_setting('active_server')

        if not active_server:
            active_server = Setting('active_server', 0)
            db_session.add(active_server)
            db_session.commit()

        else:
            active_server.value = 0
            db_session.add(active_server)
            db_session.commit()

    except:
        logger.log('Plex :: Failed to reset server, please make sure to select new one.', 'WARNING')

    # return a list of (server name, server id)
    return jsonify(success=True, servers=listServers())



@app.route('/xhr/plex/login/<username>/<password>/') # for testing purposes only
@requires_auth
def loginToPlex(username=None, password=None):
    global user
    if username is None:
        if not get_setting_value('myPlex_username') or not get_setting_value('myPlex_password'):
            logger.log('Plex :: Missing Plex Credentials in db', 'INFO')
            return False
        else:
            username = get_setting_value('myPlex_username')
            password = get_setting_value('myPlex_password')

    logger.log('Plex :: Logging into plex.tv', 'INFO')
    try:
        user = User(username, password)
        user, token = user.MyPlexSignIn()

        if user is '':
            logger.log('Plex :: Log in FAILED', 'ERROR')
            return False # failed to sign in

        setting = get_setting('myPlex_token')
        if not setting:
            setting = Setting('myPlex_token')

        setting.value = token
        db_session.add(setting)
        db_session.commit()
        logger.log('Plex :: Log in successful', 'INFO')
        return True
    except:
        logger.log('Plex :: Log in FAILED', 'ERROR')
        return False


@app.route('/xhr/plex/servers/') # for testing purposes only
def getServers():
    global user, servers
    if not get_setting_value("myPlex_token"):
        logger.log('Plex :: Cannot retrieve servers, need to sign in to plex first', 'ERROR')
        return False

    logger.log('Plex :: Getting servers from myPlex servers.xml', 'INFO')
    try:
        user = User(get_setting_value('myPlex_username'), get_setting_value('myPlex_password'), get_setting_value('myPlex_token'))
        servers = user.getServers()
    except:
        logger.log('Plex :: Failed to retrieve server information from myPlex account', 'ERROR')
        return False

    # Storing server information into db
    try:
        for server in servers:
            server['localAddresses'] = server['localAddresses'].split(',')[0]
            addServer(server['name'], server['address'], server['port'], server['scheme'], server['host'], server['localAddresses'], server['machineIdentifier'], server['createdAt'], server['updatedAt'], server['synced'], server['version'], server['owned'], server['accessToken'])
    except:
        logger.log('Plex :: Failed to store server information in database', 'ERROR')
        return False

    return servers


def addServer(name, address, port, scheme, host, localAddresses, machineIdentifier, createdAt, updatedAt, synced, version, owned, token):
    s = PlexServer.query.filter(PlexServer.machineIdentifier == machineIdentifier).first()
    if s:
        logger.log('Plex :: Updating PlexServer %s in db' %(name), 'INFO')
        s.name = name
        s.address = address
        s.port = port
        s.scheme = scheme
        s.host = host
        s.localAddresses = localAddresses
        s.machineIdentifier = machineIdentifier
        s.createdAt = createdAt
        s.updatedAt = updatedAt
        s.synced = synced
        s.version = version
        s.owned = owned
        s.token = token

    else:
        logger.log('Plex :: Adding PlexServer %s to db' %(name), 'INFO')
        s = PlexServer(
                name,
                address,
                port,
                scheme,
                host,
                localAddresses,
                machineIdentifier,
                createdAt,
                updatedAt,
                synced,
                version,
                owned,
                token,
            )

    db_session.add(s)
    db_session.commit()


def removeStaleServers(current):
    servers = PlexServer.query.order_by(PlexServer.id).all()
    for server in servers:
        if server.machineIdentifier not in current:
            db_session.delete(server)
            logger.log("Plex :: Removed %s from db as it is stale" % server, 'DEBUG')

    db_session.commit()


@app.route('/xhr/switch_server/<server_id>/')
@requires_auth
def switch_server(server_id=None):
    """
    Switches Plex servers manually.
    """
    try:
        active_server = get_setting('active_server')

        if not active_server:
            active_server = Setting('active_server', 0)
            db_session.add(active_server)
            db_session.commit()

        server = PlexServer.query.filter(PlexServer.id == server_id).first()
        if server:
            active_server.value = server_id
            db_session.add(active_server)
            db_session.commit()
            logger.log('Switched active server to ID %s' % server_id , 'INFO')
            try:
                status, msg = plex_update_sections(server_id)
                if not status:
                    logger.log('Plex :: %s' % msg, 'ERROR')
            except Exception as e:
                return jsonify(success=False, msg='Failed to reach server, please check log for details.')
        else:
            logger.log('Switching server prevented, server ID %s does not exist in db' % server_id, 'INFO')

    except Exception as e:
        logger.log('Error setting active server to ID %s: %s' % (server_id, e) , 'WARNING')
        return jsonify(success=False)

    return jsonify(success=True)


@app.route('/xhr/plex/sections/update/<int:id>/')
def json_update_sections(id):
    status, msg = plex_update_sections(id)
    return jsonify(success=status, msg=msg)

def plex_update_sections(id):
    db_section = {
        'movie': {'size': 0, 'sections': {}, 'label': 'movie', 'preferred': 0},
        'home': {'size': 0, 'sections': {}, 'label': 'home', 'preferred': 0},
        'photo': {'size': 0, 'sections': {}, 'label': 'photo', 'preferred': 0},
        'artist': {'size': 0, 'sections': {}, 'label': 'artist', 'preferred': 0},
        'show': {'size': 0, 'sections': {}, 'label': 'show', 'preferred': 0},
    }

    # attempt to get sections from server
    dbserver = PlexServer.query.filter(PlexServer.id == id).first()
    try:
        logger.log('Accessing Plex Media Server on address %s' %(dbserver.localAddresses), 'DEBUG')
        server = Server(dbserver.localAddresses, token=dbserver.token)
        sections = server.sections()
        if not sections:
            return (False, 'Failed to get sections')
    except:
        logger.log('Failed to access Plex Media Server locally, trying external address: %s' %(dbserver.host), 'DEBUG')
        try:
            server = Server(dbserver.host, token=dbserver.token)
            sections = server.sections()
            if not sections:
                return (False, 'Failed to get sections')
            else:
                logger.log('Server connected successfully, marking server as external', 'DEBUG')
                dbserver.localAddresses = dbserver.host
        except:
            return (False, 'Failed to retrieve server with id: %i' %id)

    # keeping old preferred sections
    try:
        db_section['movie']['preferred'] = dbserver.sections['movie']['preferred']
        db_section['home']['preferred'] = dbserver.sections['home']['preferred']
        db_section['photo']['preferred'] = dbserver.sections['photo']['preferred']
        db_section['artist']['preferred'] = dbserver.sections['artist']['preferred']
        db_section['show']['preferred'] = dbserver.sections['show']['preferred']
    except:
        pass

    # Go through each section and add it to new section dictionary
    try:
        for section in sections:
            if 'video' in section['thumb']:
                section['type'] = u'home'

            db_section[section['type']]['sections'].update(
                {
                    db_section[section['type']]['size']:
                    {
                        'key': section['key'],
                        'type': section['type'],
                        'title': section['title'],
                        'uuid': section['uuid']
                    }
                }
            )
            db_section[section['type']]['size'] += 1
        dbserver.sections = db_section
        db_session.add(dbserver)
        db_session.commit()
        logger.log('Plex :: Successfully updated %s sections' % server, 'INFO')
    except:
        logger.log('Plex :: Failed to update sections for server', 'ERROR')
        return (False, 'Failed to update sections for server')

    return (True, None)


@app.route('/xhr/plex/servers/list/')
def listServers(owned=False):
    servers = []

    if owned:
        dbServers = PlexServer.query.filter(PlexServer.owned == '1').all()
    else:
        dbServers = PlexServer.query.order_by(PlexServer.id).all()

    for server in dbServers:
        servers.append([server.name, server.id])

    return servers


@app.route('/xhr/plex/section/save/<type>/<int:id>/')
@requires_auth
def savePreferredSection(type, id):
    try:
        server = PlexServer.query.filter(PlexServer.id == get_setting_value('active_server')).first()
        server.sections[type]['preferred'] = int(id)
        db_session.add(server)
        db_session.commit()
        logger.log('Plex :: Changed preferred %s section to %i' %(type, id), 'INFO')
        return jsonify(success=True)
    except:
        return jsonify(success=False, msg='Failed to set preferred category')


@app.route('/xhr/plex/ping/', methods=['POST'])
def pingPlexServer():
    # user = request.form['username']
    # password = request.form['password']
    address = request.form['address']
    port = request.form['port']

    try:
        server = Server(ip=address, port=port)
        # server.setUsername(user)
        # server.setPassword(password)
        info = server.generic('')
        name = info['friendlyName']
        version = info['version']
        machineIdentifier = info['machineIdentifier']
        platform = info['platform']
        addServer(name, address, port, "http", address, address, machineIdentifier, "", "", "", version, 1, "")
        return jsonify(success=True, name=name, version=version, platform=platform, servers=listServers())
    except Exception, e:
        logger.log("Plex :: failed to query manual server: %s" % e, "ERROR")

    return jsonify(success=False)


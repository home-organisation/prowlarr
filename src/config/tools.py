import os
import logging
from operator import index

import database
import base64
import hashlib
import uuid
import pwd
import grp

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

def get_env_parameter() -> dict:
    logging.info("Get environment config variables")

    # Parameter with default value
    user = os.environ.get('USER') or "admin"
    proxyurl = os.environ.get('PROXY_URL') or "http://localhost:8191"
    proxyname = os.environ.get('PROXY_NAME') or "FlareSolverr"
    proxytag = os.environ.get('PROXY_TAG') or "flare"
    indexername = os.environ.get('INDEXER_NAME') or "YGGtorrent"
    indexerurl = os.environ.get('INDEXER_URL') or "https://www.ygg.re/"
    prowlarrurl = os.environ.get('PROWLARR_URL') or "http://prowlarr:9696"
    sonarrurl = os.environ.get('SONARR_URL') or "http://sonarr:8989"
    sonarrname = os.environ.get('SONARR_NAME') or "TVShows"
    radarrurl = os.environ.get('RADARR_URL') or "http://radarr:7878"
    radarrname = os.environ.get('RADARR_NAME') or "Films"


    # Parameter without default value
    password = os.environ.get('PASSWORD')
    indexeruser = os.environ.get('INDEXER_USER')
    indexerpassword = os.environ.get('INDEXER_PASSWORD')
    sonarrapikey = os.environ.get('SONARR_APIKEY')
    radarrapikey = os.environ.get('RADARR_APIKEY')

    # Parameter with static value


    param = {
        "user": user,
        "identifier": None,
        "salt": None,
        "password": password,
        "proxy" : {
            "name": proxyname,
            "url": proxyurl,
            "tag": proxytag,
        },
        "indexer" : {
            "name": indexername,
            "url": indexerurl,
            "user": indexeruser,
            "password": indexerpassword,
            "proxytag": proxytag,
        },
        "sonarr" : {
            "name": sonarrname,
            "url": sonarrurl,
            "apikey": sonarrapikey,
            "prowlarrurl": prowlarrurl,
            "proxytag": proxytag,
        },
        "radarr" : {
            "name": radarrname,
            "url": radarrurl,
            "apikey": radarrapikey,
            "prowlarrurl": prowlarrurl,
            "proxytag": proxytag,
        },
    }

    return param

def get_db_parameter() -> dict:
    logging.info("Get database config variables")
    user = os.environ.get('USER') or "admin"
    proxyname = os.environ.get('PROXY_NAME') or "FlareSolverr"
    indexername = os.environ.get('INDEXER_NAME') or "YGGtorrent"
    sonarrname = os.environ.get('SONARR_NAME') or "TVShows"
    radarrname = os.environ.get('RADARR_NAME') or "Films"
    dbuser = os.environ.get('DBUSER')
    dbpass = os.environ.get('DBPASS')
    dbport = os.environ.get('DBPORT')
    dbhost = os.environ.get('DBHOST')

    if dbuser is None or dbpass is None or dbport is None or dbhost is None:
        # Connection to sqlite database
        db = database.Sqlite()
        db.connect()
    else:
        # Connection to postgresql database
        db = database.Postgres()
        db.connect(user=dbuser, password=dbpass, host=dbhost ,port=dbport)

    user, identifier, salt, password = db.get_credential(user)
    proxyurl, proxytag = db.get_proxy(name=proxyname)
    indexerurl, indexeruser, indexerpassword, indexer_proxytag = db.get_indexer(name=indexername)
    sonarrurl, sonarrapikey, sonarr_prowlarrurl, sonarr_proxytag = db.get_application(name=sonarrname)
    radarrurl, radarrapikey, radarr_prowlarrurl, radarr_proxytag = db.get_application(name=radarrname)

    db.close()

    param = {
        "user": user,
        "identifier": identifier,
        "salt": salt,
        "password": password,
        "proxy": {
            "name": proxyname,
            "url": proxyurl,
            "tag": proxytag,
        },
        "indexer": {
            "name": indexername,
            "url": indexerurl,
            "user": indexeruser,
            "password": indexerpassword,
            "proxytag": indexer_proxytag,
        },
        "sonarr": {
            "name": sonarrname,
            "url": sonarrurl,
            "apikey": sonarrapikey,
            "prowlarrurl": sonarr_prowlarrurl,
            "proxytag": sonarr_proxytag,
        },
        "radarr": {
            "name": radarrname,
            "url": radarrurl,
            "apikey": radarrapikey,
            "prowlarrurl": radarr_prowlarrurl,
            "proxytag": radarr_proxytag,
        }
    }

    return param

def reconcile(desired: dict, current: dict):
    logging.info("Start to reconcile config parameter")

    # database connection
    dbuser = os.environ.get('DBUSER')
    dbpass = os.environ.get('DBPASS')
    dbport = os.environ.get('DBPORT')
    dbhost = os.environ.get('DBHOST')

    if dbuser is None or dbpass is None or dbport is None or dbhost is None:
        # Connection to sqlite database
        db = database.Sqlite()
        db.connect()
    else:
        # Connection to postgresql database
        db = database.Postgres()
        db.connect(user=dbuser, password=dbpass, host=dbhost ,port=dbport)


    # reconcile credential parameter
    if current["password"] is None:
        identifier = get_identifier()
        salt = get_salt()
    else:
        identifier = current["identifier"]
        salt = current["salt"]

    password = get_hash_password(desired["password"], salt)

    if desired["user"] != current["user"] or password != current["password"]:
        logging.info("Detection of drift for credential, reconcile the value")

        # Create new credential (current user None)
        if current["user"] is None:
            db.set_credential(username=desired["user"], identifier=identifier, salt=salt, password=password)
        # Update existing credential (current user not None)
        else:
            db.update_credential(username=desired["user"], password=password)

    # Reconcile tag parameter and get its tag id
    tagid = db.get_tag(tag=desired["proxy"]["tag"])
    if tagid is None:
        logging.info("Detection of drift for tag, reconcile the value")
        db.set_tag(tag=desired["proxy"]["tag"])
        tagid = db.get_tag(tag=desired["proxy"]["tag"])

    # Reconcile proxy parameter
    if current["proxy"] != desired["proxy"]:
        logging.info("Detection of drift for proxy, reconcile the value")
        if current["proxy"]["url"] is None:
            db.set_proxy(name=desired["proxy"]["name"], url=desired["proxy"]["url"], tagid=tagid)
        else:
            db.update_proxy(name=desired["proxy"]["name"], url=desired["proxy"]["url"], tagid=tagid)

    # Reconcile indexer parameter
    if current["indexer"] != desired["indexer"]:
        logging.info("Detection of drift for indexer, reconcile the value")
        if current["indexer"]["url"] is None:
            db.set_indexer(name=desired["indexer"]["name"], url=desired["indexer"]["url"], user=desired["indexer"]["user"], password=desired["indexer"]["password"], tagid=tagid)
        else:
            db.update_indexer(name=desired["indexer"]["name"], url=desired["indexer"]["url"], user=desired["indexer"]["user"], password=desired["indexer"]["password"], tagid=tagid)

    # Reconcile sonarr parameter
    if current["sonarr"] != desired["sonarr"]:
        logging.info("Detection of drift for sonarr, reconcile the value")
        if current["sonarr"]["url"] is None:
            db.set_application(kind="sonarr", name=desired["sonarr"]["name"], url=desired["sonarr"]["url"], apikey=desired["sonarr"]["apikey"], prowlarrurl=desired["sonarr"]["prowlarrurl"], tagid=tagid)
        else:
            db.update_application(kind="sonarr", name=desired["sonarr"]["name"], url=desired["sonarr"]["url"], apikey=desired["sonarr"]["apikey"], prowlarrurl=desired["sonarr"]["prowlarrurl"], tagid=tagid)

    # Reconcile radarr parameter
    if current["radarr"] != desired["radarr"]:
        logging.info("Detection of drift for radarr, reconcile the value")
        if current["radarr"]["url"] is None:
            db.set_application(kind='radarr', name=desired["radarr"]["name"], url=desired["radarr"]["url"], apikey=desired["radarr"]["apikey"], prowlarrurl=desired["radarr"]["prowlarrurl"], tagid=tagid)
        else:
            db.update_application(kind='radarr', name=desired["radarr"]["name"], url=desired["radarr"]["url"], apikey=desired["radarr"]["apikey"], prowlarrurl=desired["radarr"]["prowlarrurl"], tagid=tagid)

    # Reset IndexerSyncCommand task
    db.reset_task()

    db.close()


def restart():
    logging.info("Restart application")
    os.popen('s6-svc -r /var/run/s6-rc/servicedirs/svc-prowlarr/')

def get_hash_password(password: str, salt: bytes) -> bytes:
    if password is None:
        encryptpassword = None
    else:
        encryptsalt = base64.b64decode(salt)
        encryptpassword = base64.b64encode(hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), encryptsalt, 10000, 32))

    return encryptpassword

def get_salt() -> bytes:
    salt = base64.b64encode(os.urandom(16))

    return salt

def get_identifier() -> str:
    identifier = str(uuid.uuid4())

    return identifier
import logging
import sqlite3
import json
import psycopg2

SQLITE_FILE='/config/prowlarr.db'
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

class Database:
    def __init__(self):
        self.conn = None

    def close(self):
        try:
            self.conn.close()
        except (sqlite3.DatabaseError, Exception) as error:
            logging.error("Closing connection to sqlite database failed")
            logging.error(error)
        except (psycopg2.DatabaseError, Exception) as error:
            logging.error("Closing connection to postgresql database failed")
            logging.error(error)

    def get(self, query: str, data: tuple[str] = None):
        cur = self.conn.cursor()

        try:
            if data is None:
                cur.execute(query)
            else:
                cur.execute(query, data)
            row = cur.fetchone()

            return row
        except (sqlite3.DatabaseError, Exception) as error:
            logging.error("failed to get information on database")
            logging.error(error)
        except (psycopg2.DatabaseError, Exception) as error:
            logging.error("failed to get information on database")
            logging.error(error)
        finally:
            cur.close()

    def set(self, query: str, data: tuple = None):
        cur = self.conn.cursor()

        try:
            if data is None:
                cur.execute(query)
            else:
                cur.execute(query, data)
            self.conn.commit()

        except (sqlite3.DatabaseError, Exception) as error:
            logging.error("failed to set information on database")
            logging.error(error)
        except (psycopg2.DatabaseError, Exception) as error:
            logging.error("failed to set information on database")
            logging.error(error)
        finally:
            cur.close()

    def get_proxy (self, name: str):
        query = 'SELECT * FROM "IndexerProxies" WHERE "Name" = \'' + name + '\''

        row = self.get(query)
        if row is not None:
            tagid = row[5].replace('[', '').replace(']', '')
            url = json.loads(row[2])["host"]

            query = 'SELECT * FROM "Tags" WHERE "Id" = \'' + str(tagid) + '\''
            row = self.get(query)
            if row is not None:
                tag = row[1]
                return  url, tag
            else:
                return url, None
        else:
            return None, None

    def get_tag (self, tag: str):
        query = 'SELECT * FROM "Tags" WHERE "Label" = \'' + tag + '\''

        row = self.get(query)
        if row is not None:
            tagid = row[0]
            return tagid
        else:
            return None

    def set_tag (self, tag: str):
        query = 'INSERT INTO "Tags" ("Label") VALUES(\'' + tag + '\')'

        self.set(query)


    def set_proxy (self, name: str, url: str, tagid: str):
        query = 'INSERT INTO "IndexerProxies" ("Name","Settings","Implementation","ConfigContract","Tags") VALUES(\'' + name + '\', \'{ "host": "' + url + '",  "requestTimeout": 60}\', \'FlareSolverr\', \'FlareSolverrSettings\', \'[' + str(tagid) + ']\')'

        self.set(query)

    def update_proxy (self, name: str, url: str, tagid: str):
        query = 'UPDATE "IndexerProxies" SET "Settings" = \'{ "host": "' + url + '",  "requestTimeout": 60}\', "Tags" = \'[' + str(tagid) + ']\' WHERE "Name" = \'' + name + '\''

        self.set(query)

    def get_indexer (self, name: str):
        query = 'SELECT * FROM "Indexers" WHERE "Name" = \'' + name + '\''

        row = self.get(query)
        if row is not None:
            tagid = row[10].replace('[', '').replace(']', '')
            url = json.loads(row[3])["baseUrl"]
            user = json.loads(row[3])["extraFieldData"]["username"]
            password = json.loads(row[3])["extraFieldData"]["password"]

            query = 'SELECT * FROM "Tags" WHERE "Id" = \'' + str(tagid)  + '\''
            row = self.get(query)
            if row is not None:
                tag = row[1]
                return url, user, password, tag
            else:
                return url, user, password, None
        else:
            return None, None, None, None

    def set_indexer(self, name: str, url: str, user: str, password: str, tagid: str):
        # Set custom indexer
        query = 'INSERT INTO "Indexers" ("Name","Implementation","Settings","ConfigContract","Enable","Priority","Added","Redirect","AppProfileId","Tags","DownloadClientId") VALUES(\'' + name + '\', \'Cardigann\', \'{"definitionFile": "yggtorrent", "extraFieldData": {"username": "' + user + '", "password": "' + password + '", "category": 6, "subcategory": 52, "multilang": false, "multilanguage": 1, "vostfr": false, "filter_title": false, "strip_season": true, "enhancedAnime": false, "enhancedAnime4": false, "sort": 1, "type": 1 }, "baseUrl": "' + url + '", "baseSettings": { "limitsUnit": 0 }, "torrentBaseSettings": {}}\', \'CardigannSettings\', true, 25, \'2023-04-01 22:05:12.6172687Z\', false, 1, \'[' + str(tagid) + ']\', 0)'
        self.set(query)

        # Set default indexer
        query = 'INSERT INTO "Indexers" ("Name","Implementation","Settings","ConfigContract","Enable","Priority","Added","Redirect","AppProfileId","Tags","DownloadClientId") VALUES(\'The Pirate Bay\', \'Cardigann\', \'{"definitionFile": "thepiratebay", "baseUrl": "https://thepiratebay.org/", "baseSettings": { "limitsUnit": 0 }, "torrentBaseSettings": {}}\', \'CardigannSettings\', true, 40, \'2023-04-01 22:05:12.6172687Z\', false, 1, \'[]\', 0)'
        self.set(query)

    def update_indexer(self, name: str, url: str, user: str, password: str, tagid: str):
        query = 'UPDATE "Indexers" SET "Settings" = \'{"definitionFile": "yggtorrent", "extraFieldData": {"username": "' + user + '", "password": "' + password + '", "category": 6, "subcategory": 52, "multilang": false, "multilanguage": 1, "vostfr": false, "filter_title": false, "strip_season": true, "enhancedAnime": false, "enhancedAnime4": false, "sort": 1, "type": 1 }, "baseUrl": "' + url + '", "baseSettings": { "limitsUnit": 0 }, "torrentBaseSettings": {}}\', "Tags" = \'[' + str(tagid) + ']\' WHERE "Name" = \'' + name + '\''

        self.set(query)

    def get_application(self, name: str):
        query = 'SELECT * FROM "Applications" WHERE "Name" = \'' + name + '\''

        row = self.get(query)
        if row is not None:
            tagid = row[6].replace('[', '').replace(']', '')
            url = json.loads(row[3])["baseUrl"]
            apikey = json.loads(row[3])["apiKey"]
            prowlarrurl = json.loads(row[3])["prowlarrUrl"]

            query = 'SELECT * FROM "Tags" WHERE "Id" = \'' + str(tagid)+ '\''
            row = self.get(query)
            if row is not None:
                tag = row[1]
                return url, apikey, prowlarrurl, tag
            else:
                return url, apikey, prowlarrurl, None
        else:
            return  None, None, None, None

    def set_application(self, kind:str, name: str, url: str, apikey: str, prowlarrurl: str, tagid: str):
        # Set custom application
        if kind == 'radarr':
            query = 'INSERT INTO "Applications" ("Name","Implementation","Settings","ConfigContract","SyncLevel","Tags") VALUES(\'' + name + '\', \'Radarr\', \'{"prowlarrUrl": "' + prowlarrurl + '", "baseUrl": "' + url + '", "apiKey": "' + apikey + '", "syncCategories": [2000,2010,2020,2030,2040,2045,2050,2060,2070,2080]}\', \'RadarrSettings\', 2, \'[' + str(tagid) + ']\')'
        else:
            query = 'INSERT INTO "Applications" ("Name","Implementation","Settings","ConfigContract","SyncLevel","Tags") VALUES(\'' + name + '\', \'Sonarr\', \'{"prowlarrUrl": "' + prowlarrurl + '", "baseUrl": "' + url + '", "apiKey": "' + apikey + '", "syncCategories": [5000,5010,5020,5030,5040,5045,5050], "animeSyncCategories": [5070], "syncAnimeStandardFormatSearch": true}\', \'SonarrSettings\', 2, \'[' + str(tagid) + ']\')'
        self.set(query)

        # Set default application
        if kind == 'radarr':
            query = 'INSERT INTO "Applications" ("Name","Implementation","Settings","ConfigContract","SyncLevel","Tags") VALUES(\'' + name + ' (not flare)\', \'Radarr\', \'{"prowlarrUrl": "' + prowlarrurl + '", "baseUrl": "' + url + '", "apiKey": "' + apikey + '", "syncCategories": [2000,2010,2020,2030,2040,2045,2050,2060,2070,2080]}\', \'RadarrSettings\', 2, \'[]\')'
        else:
            query = 'INSERT INTO "Applications" ("Name","Implementation","Settings","ConfigContract","SyncLevel","Tags") VALUES(\'' + name + ' (not flare)\', \'Sonarr\', \'{"prowlarrUrl": "' + prowlarrurl + '", "baseUrl": "' + url + '", "apiKey": "' + apikey + '", "syncCategories": [5000,5010,5020,5030,5040,5045,5050], "animeSyncCategories": [5070], "syncAnimeStandardFormatSearch": true}\', \'SonarrSettings\', 2, \'[]\')'
        self.set(query)

    def update_application(self, kind: str, name: str, url: str, apikey: str, prowlarrurl: str, tagid: str):
        if kind == 'radarr':
            query = 'UPDATE "Applications" SET "Settings" = \'{"prowlarrUrl": "' + prowlarrurl + '", "baseUrl": "' + url + '", "apiKey": "' + apikey + '", "syncCategories": [2000,2010,2020,2030,2040,2045,2050,2060,2070,2080]}\', "Tags" = \'[' + str(tagid) + ']\' WHERE "Name" = \'' + name + '\''

        else:
            query = 'UPDATE "Applications" SET "Settings" = \'{"prowlarrUrl": "' + prowlarrurl + '", "baseUrl": "' + url + '", "apiKey": "'+ apikey + '", "syncCategories": [5000,5010,5020,5030,5040,5045,5050], "animeSyncCategories": [5070], "syncAnimeStandardFormatSearch": true}\', "Tags" = \'[' + str(tagid) + ']\' WHERE "Name" = \'' + name + '\''

        self.set(query)

    def reset_task(self):
        query = 'UPDATE "ScheduledTasks" SET "LastExecution" = \'0001-01-01 00:00:00Z\', "LastStartTime" = null WHERE "TypeName" = \'NzbDrone.Core.Applications.ApplicationIndexerSyncCommand\''

        self.set(query)


class Postgres(Database):
    def connect(self, user: str, password: str, host: str, port: str):
        # connecting to PostgreSQL database
        try:
            self.conn = psycopg2.connect(database="prowlarr-main", user=user, password=password, host=host, port=port)
        except (psycopg2.DatabaseError, Exception) as error:
            logging.error("Connection to postgresql database failed")
            logging.error(error)

    def get_credential(self,username: str):
        data = (username,)
        query = 'SELECT "Identifier", "Salt", "Password" FROM "Users" WHERE "Username" = %s'

        row = self.get(query, data)
        if row is not None:
            return username, row[0], row[1].encode(), row[2].encode()
        else:
            return None, None, None, None

    def set_credential(self,username: str, identifier: str, salt: bytes, password: bytes):
        data = (identifier, username, password.decode(), salt.decode(), 10000)
        query = 'INSERT INTO "Users" ("Identifier", "Username", "Password", "Salt", "Iterations") VALUES(%s, %s, %s, %s, %s)'

        self.set(query, data)

    def update_credential(self,username: str, password: bytes):
        data = (password.decode(), username)
        query = 'UPDATE "Users" SET "Password" = %s WHERE "Username" = %s'

        self.set(query, data)


class Sqlite(Database):
    def connect(self):
        # connection to sqlite database
        try:
            self.conn = sqlite3.connect(SQLITE_FILE)
        except (sqlite3.DatabaseError, Exception) as error:
            logging.error("Connection to sqlite database failed")
            logging.error(error)

    def get_credential(self,username: str):
        data = (username,)
        query = 'SELECT "Identifier", "Salt", "Password" FROM "Users" WHERE "Username" = ?'

        row = self.get(query, data)
        if row is not None:
            return username, row[0], row[1], row[2]
        else:
            return None, None, None, None

    def set_credential(self,username: str, identifier: str, salt: bytes, password: bytes):
        data = (identifier, username, password, salt, 10000)
        query = 'INSERT INTO "Users" ("Identifier", "Username", "Password", "Salt", "Iterations") VALUES(?, ?, ?, ?, ?)'

        self.set(query, data)

    def update_credential(self,username: str, password: bytes):
        data = (password, username)
        query = 'UPDATE "Users" SET "Password" = ? WHERE "Username" = ?'

        self.set(query, data)
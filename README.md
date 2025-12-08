[![Docker Repository on Quay](https://quay.io/repository/bizalu/prowlarr/status "Docker Repository on Quay")](https://quay.io/repository/bizalu/prowlarr)
[![Codefresh build status]( https://g.codefresh.io/api/badges/pipeline/homeorga/media-core%2Fbuild?type=cf-1&key=eyJhbGciOiJIUzI1NiJ9.NjQ4MjRkOGYyNDA0MzM1ZDdmNGZjZjBj.AUF1y_T4njx5CHlXS1tyIRLP-M_D9iyoHdLG08i5xek)]( https://g.codefresh.io/pipelines/edit/new/builds?id=66854e40bd4d8040b129415d&pipeline=build&projects=media-core&projectId=6482e65b2eca974dcb834aa3)

# Prowlarr
This docker image is a custom image of prowlarr based on lscr.io/linuxserver/prowlarr.

# Parameters
Container images are configured using parameters passed at runtime has environment variable. 

The parameters below are taken from the original image [lscr.io/linuxserver/prowlarr](https://hub.docker.com/r/linuxserver/prowlarr) :

| Parameters  | Examples values   | Functions                                                                                                     |
|-------------|-------------------|---------------------------------------------------------------------------------------------------------------|
| PUID        | 1000              | for UserID                                                                                                    |
| PGID        | 1000              | for GroupID                                                                                                   |
| TZ          | Europe/Paris      | Specify a timezone to use, see this [List](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List) |



The extra parameters below come from this custom image :
- Prowlarr parameters :

| Parameters       | Examples values   | Functions                                                                                |
|------------------|-------------------|------------------------------------------------------------------------------------------|
| AUTHMETHOD       | Forms (default)   | Authentication method for web authentication. Acceptable value is **Forms** or **Basic** |
| URLBASE         | /proxy (optional) | Base URL for Prowlarr web interface                                                      |
| USER             | admin (default)   | Username for web authentication                                                          |
| PASSWORD         | ****              | Password for web authentication                                                          |
| APIKEY           | ****              | Key for api authentication                                                               |

- Proxy (Flaresolverr) parameters :

| Parameters       | Examples values                 | Functions                                                                                |
|------------------|---------------------------------|------------------------------------------------------------------------------------------|
| PROXY_URL        | http://localhost:8191 (default) | FlareSolverr Indexer Proxy URL                                                           |
| PROXY_NAME       | FlareSolverr (default)          | FlareSolverr Indexer Proxy name                                                          |
| PROXY_TAG        | flare (default)                 | FlareSolverr Indexer Proxy tag                                                           |

- Indexer (only YGGtorrent is supported) parameters :

| Parameters       | Examples values                 | Functions                                                                                |
|------------------|---------------------------------|------------------------------------------------------------------------------------------|
| INDEXER_URL      | https://www.ygg.re/ (default)   | YGGtorrent indexer URL                                                                   |
| INDEXER_NAME     | YGGtorrent (default)            | YGGtorrent indexer name                                                                  |
| INDEXER_USER     | ****                            | YGGtorrent indexer user                                                                  |
| INDEXER_PASSWORD | ****                            | YGGtorrent indexer password                                                              |

- Application (sonarr and radarr) parameters :

| Parameters    | Examples values                | Functions                                   |
|---------------|--------------------------------|---------------------------------------------|
| PROWLARR_URL  | http://prowlarr:9696 (default) | Application Prowlarr URL use by application |
| SONARR_URL    | http://sonarr:8989 (default)   | Application Sonarr URL                      |
| SONARR_NAME   | TVShows (default)              | Application Sonarr name                     |
| SONARR_APIKEY | ****                           | Application Sonarr apikey                   |
| RADARR_URL    | http://radarr:7878 (default)   | Application Radarr URL                      |
| RADARR_NAME   | "Films" (default)              | Application Radarr name                     |
| RADARR_APIKEY | ****                           | Application Radarr apikey                   |

- Database parameters (if not set, sqlite will be used) :

|  Parameters          | Examples values       | Functions                                                  |
|----------------------|-----------------------|------------------------------------------------------------|
| DBUSER               | prowlarr (optional)   | Database - postgresql username                             |
| DBPASS               | **** (optional)       | Database - postgresql password                             |
| DBPORT               | 5432 (optional)       | Database - postgresql port                                 |
| DBHOST               | postgresql (optional) | Database - postgresql host                                 |
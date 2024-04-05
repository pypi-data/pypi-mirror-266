import os
home_dir = os.path.expanduser('~')

JFROG_CLI_CONFIG_FILE_PATH = os.path.join(home_dir, '.jfrog', 'jfrog-cli.conf.v6')
CONFIG_FILE_PATH = os.path.join(home_dir, '.frogml','config.json')

FROG_ML_CONFIG_USER = 'user'
FROG_ML_CONFIG_ARTIFACTORY_URL = 'artifactory_url'
FROG_ML_CONFIG_PASSWORD = 'password'
FROG_ML_CONFIG_ACCESS_TOKEN = 'access_token'
SERVER_ID = 'server_id'

JFROG_CLI_CONFIG_ARTIFACTORY_URL = 'artifactoryUrl'
JFROG_CLI_CONFIG_URL = 'url'
JFROG_CLI_CONFIG_USER = 'user'
JFROG_CLI_CONFIG_PASSWORD = 'password'
JFROG_CLI_CONFIG_ACCESS_TOKEN = 'accessToken'

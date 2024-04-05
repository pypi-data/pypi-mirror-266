# JFrog ML (frogML)

## Table of contents:

- [Overview](#Overview)
- [Build](#Build)
- [Login to Artifactory](#Login-to-Artifactory)
- [Upload ML model to Artifactory](#Upload-ML-model-to-Artifactory)
- [Upload ML model auxiliary files to Artifactory](#Upload-ML-model-auxiliary-files-to-Artifactory)
- [Download ML model from Artifactory](#Download-ML-model-from-Artifactory)

### Overview

JFrog ML (jfrogml) is a smart python client library provides a simple method of storing and downloading models and model
data from the JFrog platform, utilizing the advanced capabilities of the JFrog platform

### Package Build

```
python3 -m build
```

#### Run CI

#### Locally run tests using artifactory docker

To run the tests, use the ```make test``` command which start an Artifactory container, create a local repository in
it, generate a user token, and runs the test using the generated token

#### Locally run tests using exiting Artifacotry

To run the tests, use the ```pytest``` command pointing it to an existing Artifactory host, select a generic local
repository in
, generate a user token or provide user credentials , and runs the test:

```
python3 -m  pytest tests/integrations/test_artifactory_integration.py  --rt_host "<RT host>" --rt_token <token>   --repo_name <generic-repo-name> -s
alternatively use --rt_user <username>  and --rt_password <password> instead of --rt_token
```

### Login to Artifactory

To be able to use frogml in front of Artifactory, you should authenticate the frogml client against Artifactory.
There are 2 main ways to authenticate:

1. Login via cli.
2. Login by adding authentication details to your python script.

#### Login via cli

It is possible to authenticate the frogml client via cli by two flows:

1. Login by one command line flow
2. Interactive flow

At the end of each login attempt, the authentication result (success or failure) is printed on the screen.
If the login attempt succeeded, the authentication details will be saved as frogml configuration under the path:
~/.frogml/config.json

In both 'interactive flow' and the 'one command flow', it is possible to authenticate the frogml client by:

1. username and password
2. Access token
3. Anonymous authentication

#### Login by one command line with options

The below examples show the frogml login examples by the cli:

Login by existing frogml configuration: ~/.frogml/config.json

```
frogml login
```

Login by the username password:

```
frogml login --url <artifactory_url> --username <username> --password <password>
```

Login by the Access token:

```
frogml login --url <artifactory_url> --token <access_token> 
```

Login by anonymous access:

```
frogml login --url <artifactory_url> --anonymous
```

#### Login by interactive flow in Cli:

For starting an interactive flow in the cli, run the command:

```
frogml login --interactive
```

After typing the command above, the cli will suggest you two options: authenticate by the jfrog-cli configuration or
connecting to a new server:

```
frogml login --interactive
Please select from the following options:
1.Login by jfrog-cli configuration file: ~/.jfrog/jfrog-cli.conf.v6
2.Connecting to a new serve
```

by selecting the first option, the frogml client tries to read the jfrog-cli configuration file that should be stored at
~/.jfrog/jfrog-cli.conf and to send a ping to Artifactory with the authentication details from the file.

By selecting the second option, the cli asks the user to insert the artifactory url and then to choose the desired
authentication method:

```
Enter artifactory base url: http://localhost:8082
Choose your preferred authentication option:
0: Username and Password
1: Access Token
2: Anonymous Access
:
```

#### Login by adding authentication details to script

The below examples show how to add authentication details in the code:

Authentication by username and password:

```
from jfrog_ml.frog_ml import FrogML
from jfrog_ml.authentication.models._auth_config import AuthConfig

arti = FrogML(AuthConfig.by_basic_auth("http://localhost:8082", <username>, <password>))
```

Authentication by access token:

```
from jfrog_ml.frog_ml import FrogML
from jfrog_ml.authentication.models._auth_config import AuthConfig

arti = FrogML(AuthConfig.by_access_token("http://localhost:8082", <token>))
```

#### Upload ML model to Artifactory

To upload, it is possible to mention version or not to specify it, in case the version is not specified the model will
be saved under the upload date folder in the repository.
It is possible to add properties on the model in Artifactory.

The below examples show how to upload a model to Artifactory:

Upload a model as an entire folder

```
from jfrog_ml.frog_ml import FrogML

arti = FrogML()
arti.upload_model_version(repository=<repository_key>, namespace=<namespce>, model_name=<model_name>,
                          source_path="~/model_to_upload/",
                          properties={"model_type": "kerras", "experiment": "my-exp"})
```

Upload a model which specified version

```
from jfrog_ml.frog_ml import FrogML

arti = FrogML()
arti.upload_model_version(repository=<repository_key>, namespace=<namespce>, model_name=<model_name>, version=<version>
                          ,source_path="~/model_to_upload/config.json")
```

Upload a model as a single file:

```
from jfrog_ml.frog_ml import FrogML

arti = FrogML()
arti.upload_model_version(repository=<repository_key>, namespace=<namespce>, model_name=<model_name>, version=<version>
                          ,source_path="~/model_to_upload/config.json")
```

#### Upload ML model auxiliary files to Artifactory

To upload local auxiliary artifacts and attach them to an existing model version, use the upload_auxiliary_artifacts:

* version is required

```
from jfrog_ml.frog_ml import FrogML

artifactory = FrogML()

artifactory.upload_auxiliary_artifacts(repository=<repository_key>,  namespace=<namespce>, model_name=<model_name>,
                                       source_path="~/auxiliary_artifacts",
                                       version=<version>)
```

Upload a single auxiliary file:

* version is required

```
from jfrog_ml.frog_ml import FrogML

artifactory = FrogML()

artifactory.upload_auxiliary_artifacts(repository=<repository_key>, namespace=<namespce>, model_name=<model_name>,
                                       source_path="~/auxiliary_artifacts/config.json",
                                       version=<version>)
```

#### Download ML model from Artifactory

The below example shows how to download a model from Artifactory:

```
from jfrog_ml.frog_ml import FrogML

arti = FrogML()

arti.download_model_version(repository=<repository_key>, namespace=<namespace>, model_name=<model_name>,
                            target_path="~/models", version=<version>)
```
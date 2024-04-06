# ceotr_config

This library assists the CEOTR data team in establishing a standardized method for setting up project configurations.

## Installation

```bash
pip install ceotr_config
```


```python
from ceotr_config import config_agenet

SETTING_PATH = "path_to_your_setting"
SETTING_TEMPLATE_PATH = "path_to_YML_template"
PATH_TO_DOCKER="PATH_TO_YOUR_DOT_ENV_FILE"
PROJECT_ROOT="PATH_TO_THE_PROJECT_ROOT"

# if this is a Python project only
# it will auto generate  setting YML from setting template if it not alreadt exist
config_agenet.load(setting_path = SETTING_PATH, setting_template=SETTING_TEMPLATE_PATH)

# if this is a docker python project
# make sure in your environment variable ENVIRONMENT=docker, otherwise
# it won't read config from .env
config_agenet.load(setting_path = SETTING_PATH, setting_template=SETTING_TEMPLATE_PATH, docker_dot_env_path=PATH_TO_DOCKER)
#or
config_agenet.load(setting_path = SETTING_PATH, setting_template=SETTING_TEMPLATE_PATH, project_root=PATH_TO_DOCKER)

# if you give variable from docker_dot_env_path, it will read value from docker_dot_env_path
# if you specific value for project_root and not for docker_dot_env_path, it will assign docker_dot_env_path as {project_root}/docker/.env
```


# update the PyPI

## This repo will auto update the PyPI package when there is a push to master
### for trouble shooting look at steps below
- Check `~/resources/dinkum/.pypirc` on the ceotr dev server, ensure it's present and contains the correct token

### To update the dinkum package on PyPI **manually** you will need to do the following:
- ensure the python package "twine" is installed using `pip install twine`
- change the version number in [version/__init__.py](version/__init__.py)
- run the following commands:
    - `python setup.py sdist`
    - `twine upload dist/*`
- enter the CEOTR PyPI username and password, or use token authentication

For CI, it will auto release the library to PyPi while there is new tag created



[![Coverage](http://129.173.20.172:9000/api/project_badges/measure?project=ceotr-public_ceotr_app_common_ceotr_config_608ff53d-9e27-4857-bb53-9cb5609b0f96&metric=coverage&token=sqb_fac9c74ea6746cafd20cb09c9f20d9e19c01508d)](http://129.173.20.172:9000/dashboard?id=ceotr-public_ceotr_app_common_ceotr_config_608ff53d-9e27-4857-bb53-9cb5609b0f96)
from typing import List, Optional

import typer

from jfrog_ml._utils import join_url, assembly_artifact_url
from jfrog_ml.authentication._authentication_utils import parse_cli_config_server, read_jfrog_cli_config, \
    get_frogml_configuration
from jfrog_ml.authentication.models._auth_config import AuthConfig
from jfrog_ml.cli.utils._login_checks_utility import is_login_command_without_params, login_input_checks
from jfrog_ml.cli.models._cli_login_arguments import LoginArguments
from jfrog_ml.cli.utils._cli_utils import get_list_of_servers_from_config
from jfrog_ml.cli.commands._login_command import run as run_login
from jfrog_ml.constants import JFROG_CLI_CONFIG_FILE_PATH, CONFIG_FILE_PATH


def login(url: Optional[str], username: Optional[str], password: Optional[str], token: Optional[str],
          anonymous: Optional[bool], is_interactive: Optional[bool]):
    if is_login_command_without_params(url, username, password, token, anonymous):
        if not is_interactive:
            return __login_by_frogml_configuration_file_flow()
        else:
            return __interactive_flow()
    elif login_input_checks(url, username, password, token, anonymous):
        url = assembly_artifact_url(url)
        return __login_by_command_line_params(url, username, password, token, anonymous)
    else:
        typer.echo(f"{__get_failed_reason(url, username, password, token, anonymous)}Login failed")


def __get_failed_reason(url: Optional[str], username: Optional[str], password: Optional[str], token: Optional[str],
                        anonymous: Optional[bool]) -> str:
    details = ''
    if url is None:
        details += "Url is required.\n"
    if token is not None and (any(params is not None for params in [username, password])):
        details += "Token is specified when username/password is specified.\n"
    if anonymous is True and any(params is not None for params in [username, password, token]):
        details += "Anonymous is specified with authentication details.\n"
    if username is None and password is not None:
        details += "Username is required when password is specified.\n"
    elif username is not None and password is None:
        details += "Password is required when username is specified.\n"
    return details


def __run_interactive_mode() -> LoginArguments or None:
    jfrog_cli_config = read_jfrog_cli_config()
    jfrog_cli_servers = get_list_of_servers_from_config(jfrog_cli_config)
    if jfrog_cli_servers is not None and len(jfrog_cli_servers) > 0:
        login_method_id = typer.prompt(f'Please select from the following options:\n'
                                       f'1.Login by jfrog-cli configuration file: {JFROG_CLI_CONFIG_FILE_PATH}\n'
                                       f'2.Connecting to a new server\n')

        while not login_method_id.isdigit() or int(login_method_id) > 2 or int(login_method_id) <= 0:
            login_method_id = typer.prompt(f"Bad Input. Choose your preferred login option")

        login_method_id = int(login_method_id)
        if login_method_id == 1:
            return __prompt_jfrog_cli_configuration_list(jfrog_cli_config, jfrog_cli_servers)

    return __prompt_manual_details()


def __prompt_manual_details() -> LoginArguments or None:
    login_args = LoginArguments()
    login_args.artifactory_url = typer.prompt("Enter artifactory base url")
    login_args.artifactory_url = join_url(login_args.artifactory_url, "artifactory")
    auth_options = ["Username and Password", "Access Token", "Anonymous Access"]
    authentication_types = ''
    for index, item in enumerate(auth_options):
        authentication_types += f"{index}: {item} \n"
    selected_auth_type = typer.prompt(f"Choose your preferred authentication option:\n{authentication_types}")
    while not selected_auth_type.isdigit() or int(selected_auth_type) >= len(auth_options) or int(
            selected_auth_type) < 0:
        selected_auth_type = typer.prompt(f"Bad Input. Choose your preferred authentication")
    selected_auth_type = int(selected_auth_type)
    if selected_auth_type == 0:
        return __prompt_username_password(login_args)
    elif selected_auth_type == 1:
        return __prompt_access_token(login_args)
    elif selected_auth_type == 2:
        login_args.isAnonymous = True
        return login_args


def __prompt_username_password(login_args: LoginArguments):
    username = typer.prompt("Enter JFrog user name")
    password = typer.prompt("Enter JFrog password", hide_input=True)
    login_args.username = username
    login_args.password = password
    return login_args


def __prompt_access_token(login_args: LoginArguments):
    token = typer.prompt("Enter JFrog access token", hide_input=True)
    login_args.access_token = token
    return login_args


def __prompt_jfrog_cli_configuration_list(jfrog_cli_config, jfrog_cli_servers: List[str]) -> LoginArguments:
    list_server_options = ''
    for index, item in enumerate(jfrog_cli_servers):
        list_server_options += f"{index}: {item}\n"
    server_index_cli_conf = typer.prompt(
        f"Found the following servers in your JFrog CLI configuration, "
        f"choose one of the following:\n{list_server_options}")
    while not server_index_cli_conf.isdigit() or int(server_index_cli_conf) < 0 or int(server_index_cli_conf) >= len(
            jfrog_cli_servers):
        server_index_cli_conf = typer.prompt("Invalid choice. Please choose a number from the list")
    server_index_cli_conf = int(server_index_cli_conf)
    typer.echo(f"{jfrog_cli_servers[server_index_cli_conf]} was chosen")
    return parse_cli_config_server(jfrog_cli_config.get("servers")[server_index_cli_conf])


def __execute_login(auth_config: AuthConfig, anonymous: bool) -> bool:
    if run_login(auth_config, anonymous):
        typer.echo(f"Logged in successfully to: {auth_config.artifactory_url.replace('/artifactory', '')}")
        return True
    else:
        typer.echo("Failed to login, bad authentication")
        return False


def __login_by_frogml_configuration_file_flow() -> bool:
    login_args = get_frogml_configuration()
    auth_config = None
    if login_args is not None:
        typer.echo(f"Using existing frogml authentication config file: {CONFIG_FILE_PATH}")
        auth_config = AuthConfig(artifactory_url=login_args.artifactory_url, user=login_args.username,
                                 password=login_args.password, access_token=login_args.access_token)

    if auth_config is not None and __execute_login(auth_config, login_args.isAnonymous):
        return True

    return __interactive_flow()


def __interactive_flow() -> bool:
    login_args = __run_interactive_mode()
    if login_args is not None:
        auth_config = AuthConfig(artifactory_url=login_args.artifactory_url, user=login_args.username,
                                 password=login_args.password, access_token=login_args.access_token)
        return __execute_login(auth_config, login_args.isAnonymous)
    return False


def __login_by_command_line_params(url, username, password, token, anonymous) -> bool:
    auth_config = AuthConfig(artifactory_url=url, user=username, password=password, access_token=token)
    return __execute_login(auth_config, anonymous)

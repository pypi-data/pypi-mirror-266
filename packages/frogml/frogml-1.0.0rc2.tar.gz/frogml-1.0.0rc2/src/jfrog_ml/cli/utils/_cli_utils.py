from typing import List


def get_list_of_servers_from_config(jfrog_cli_config) -> List[str]:
    if jfrog_cli_config is not None and jfrog_cli_config.get("servers") is not None:
        return list(map(__map_server_ids, jfrog_cli_config.get("servers")))
    return []


def __map_server_ids(server: dict):
    server_id = ''
    if server is not None:
        server_id = str(server.get("serverId"))
        if server.get("isDefault") is not None and bool(server.get("isDefault")):
            server_id = server_id + " (Default)"
    return server_id

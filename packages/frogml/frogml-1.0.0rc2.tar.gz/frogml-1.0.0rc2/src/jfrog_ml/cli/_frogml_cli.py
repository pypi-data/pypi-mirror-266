import typer
from typing_extensions import Annotated
from jfrog_ml.cli._login_cli import login as prompt_login

app = typer.Typer()


@app.command("login")
def login(url: Annotated[str, typer.Option(
    help="Artifactory base url")] = None,
          username: Annotated[str, typer.Option(help="The user's username")] = None,
          password: Annotated[str, typer.Option(help="The user's password")] = None,
          token: Annotated[str, typer.Option(help="Access token to authenticate")] = None,
          anonymous: Annotated[bool, typer.Option(help="Run login as anonymous user")] = False,
          interactive: Annotated[bool, typer.Option(help="Login with interactive flow")] = False):
    prompt_login(url, username, password, token, anonymous, interactive)


@app.callback()
def callback():
    pass


def main():
    app()


if __name__ == '__main__':
    main()

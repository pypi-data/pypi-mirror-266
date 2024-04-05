import click
import os

from meerkat import email as send_email, ping as send_ping, sms as send_sms
from meerkat.api import get_user_token

@click.group()
def meerkat():
    pass

@meerkat.command()
def ping():
    send_ping()

@meerkat.command()
@click.argument('message', type=str)
def email(message):
    send_email(message=message)

@meerkat.command()
@click.argument('message', type=str)
def sms(message):
    send_sms(message=message)

@meerkat.command()
def login():
    email = click.prompt("Enter Email")
    password = click.prompt("Enter Password", hide_input=True)
    token = get_user_token(email, password)

    if not token:
        click.echo("Invalid email or password.")
        return

    #save token to user HOME and set OS env
    with open(os.path.expanduser("~") + "/.meerkat", "w") as file:
        file.write(token)
    os.environ["MEERKAT_TOKEN"] = token

    click.echo(f"\nMeerkatIO initialized successfully!")

if __name__ == "__main__":
    meerkat()
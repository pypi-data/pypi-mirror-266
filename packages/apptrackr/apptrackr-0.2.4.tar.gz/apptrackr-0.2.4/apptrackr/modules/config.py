import configparser
import os
import typer


config = typer.Typer()

BASE_PATH = os.path.join(
    os.path.expanduser("~"), r"Library/Application Support/apptrackr.toml"
)


@config.command()
def set_recommendations() -> None:
    config = configparser.ConfigParser()
    config.read(BASE_PATH)
    if config.has_option("NETWORK", "enable-recommendations"):
        config.remove_option("NETWORK", "enable-recommendations")
    else:
        config.set("NETWORK", "enable-recommendations", "true")

    with open(BASE_PATH, "w+") as f:
        config.write(f)

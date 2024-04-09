import argparse
import logging
import platform
from pathlib import Path

from handlers import (
    ask_for_config,
    generate_certificate,
    get_config,
    get_idp,
    get_provisioner_config,
    initiate_device_code_flow,
    logger,
    poll_dev_auth_response,
    save_config,
    show_link,
)
from platform_handler import (
    PlatformHandler,
    UnixPlatformHandler,
    WindowsPlatformHandler,
)

parser = argparse.ArgumentParser()
parser.add_argument(
    "-ec",
    "--edit-config",
    help="Edit the configuration",
    action="store_true",
)

APP_NAME = "ssh-ca-cli"
DEFAULT_SCOPES = "openid"

app_dir = Path.home() / f".{APP_NAME}"

app_dir_path = Path(app_dir)
default_config_path = app_dir_path / "config.json"


def generate_cert(
    config_path: Path,
    os_handler: PlatformHandler,
):
    logger.debug(f"Reading from config file: {config_path}")

    config = get_config(config_path)

    if not config:
        config = ask_for_config()
        save_config(
            config_path,
            config,
        )

    idp = get_idp(
        config["ca_url"],
    )

    provisioner_config = get_provisioner_config(idp)

    device_init_auth_response = initiate_device_code_flow(
        idp,
        provisioner_config,
        DEFAULT_SCOPES,
    )

    show_link(device_init_auth_response)

    authentication_response = poll_dev_auth_response(
        idp,
        provisioner_config,
        device_init_auth_response,
    )

    generate_certificate(
        authentication_response,
        config["ca_url"],
        os_handler,
    )


def edit_config(
    config_file: Path = default_config_path,
):
    config_path = Path(config_file)
    config_path.expanduser()
    config = ask_for_config()
    save_config(config_path, config)


def do_generate_cert(
    config_file: Path = default_config_path,
    log_level: str = "WARNING",
):
    logger.setLevel(level=logging.getLevelName(log_level))

    os_name = platform.system().lower()

    if os_name == "windows":
        os_handler = WindowsPlatformHandler(app_dir_path)
    else:
        os_handler = UnixPlatformHandler(app_dir_path)

    generate_cert(
        config_file,
        os_handler,
    )


def entrypoint():
    args = parser.parse_args()

    if args.edit_config:
        edit_config()

    do_generate_cert()


if __name__ == "__main__":
    entrypoint()

import json
import os
import sys
import time
from pathlib import Path

from platform_handler import PlatformHandler
from requests_wrapper import HTTPRequestException, ResponseIsNotJson, requests


def get_config(config_path):
    if config_path.exists():
        with open(config_path, "r") as fp:
            return json.load(fp)

    return None


def save_config(config_path: Path, config_json):
    os.makedirs(config_path.parent, exist_ok=True)
    with open(config_path, "w") as fp:
        json.dump(config_json, fp, indent=2)
        fp.write("\n")


def ask_for_config():
    ca_url = input("Certificate Authority URL: ")

    return {
        "ca_url": ca_url,
    }


def get_idp(ca_url):
    try:
        response = requests.get(f"{ca_url}/config")
    except HTTPRequestException:
        print("Unable to retrieve provisioner config from URL provided!")
        sys.exit(-1)

    if not response.is_successful():
        print("Unable to retrieve provisioner config from URL provided!")
        sys.exit(-1)

    try:
        return response.json()
    except ResponseIsNotJson:
        print("Response for provisioner config is not valid!")
        sys.exit(-1)


def get_provisioner_config(idp):
    config_url = idp["ConfigEndpoint"]

    try:
        response = requests.get(config_url)
    except HTTPRequestException:
        print("Unable to retrieve IDP config from URL provided!")
        sys.exit(-1)

    if not response.is_successful():
        print("Unable to retrieve IDP config from URL provided!")
        sys.exit(-1)

    try:
        return response.json()
    except ResponseIsNotJson:
        print("Response for IDP config is not valid!")
        sys.exit(-1)


def initiate_device_code_flow(idp, provisioner_config, scopes):
    dev_auth_endpoint = provisioner_config["device_authorization_endpoint"]
    client_id = idp["ClientID"]

    try:
        response = requests.post(
            dev_auth_endpoint,
            body={
                "client_id": client_id,
                "scope": scopes,
            },
        )
    except HTTPRequestException:
        print("Unable to initiate device code flow!")
        sys.exit(-1)

    if not response.is_successful():
        print("Unable to initiate device code flow!")
        sys.exit(-1)

    try:
        return response.json()
    except ResponseIsNotJson:
        print("Response device code flow is not valid!")
        sys.exit(-1)


def show_link(device_init_auth_response):
    complete_uri = device_init_auth_response["verification_uri_complete"]

    print(f"Please go here to complete the authentication process: {complete_uri}")


def poll_dev_auth_response(idp, provisioner_config, dev_auth_response):
    client_id = idp["ClientID"]

    device_code = dev_auth_response["device_code"]
    token_endpoint = provisioner_config["token_endpoint"]

    try_count = 0
    max_try = 120
    sleep_secs = 2

    while try_count < max_try:
        time.sleep(sleep_secs)

        try:
            response = requests.post(
                token_endpoint,
                body={
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": device_code,
                    "client_id": client_id,
                },
            )
        except HTTPRequestException:
            print("Unable to verify authentication!")
            sys.exit(-1)

        if response.is_successful():
            try:
                return response.json()
            except ResponseIsNotJson:
                print("Response for authentication verification is not valid!")
                sys.exit(-1)

    print("Authentication timeout! Please try again.")
    sys.exit(-1)


def generate_key_files(os_handler: PlatformHandler, ca_url):
    key_type = "ed25519"
    ssh_dir = os_handler.get_ssh_file_directory(ca_url, key_type)

    os_handler.generate_key_files(key_type, ssh_dir)

    with open(f"{ssh_dir}/id_{key_type}.pub", "r") as file:
        public_key = file.read()

    return ssh_dir, key_type, public_key


def generate_certificate(
    authentication_response,
    ca_url,
    os_handler: PlatformHandler,
):
    access_token = authentication_response["access_token"]

    ssh_folder, key_type, pub_key = generate_key_files(os_handler, ca_url)

    sign_url = f"{ca_url}/sign"

    try:
        response = requests.post(
            sign_url,
            body={
                "PublicKey": pub_key,
                "OTT": access_token,
            },
            is_json=True,
        )
    except HTTPRequestException:
        print("Unable to initiate device code flow!")
        sys.exit(-1)

    if not response.is_successful():
        print("Unable to initiate device code flow!")
        sys.exit(-1)

    os_handler.generate_cert_file_content(
        ssh_folder,
        key_type,
        response.text,
    )

    os_handler.prepare_ssh_agent(
        ssh_folder,
        key_type,
    )

    print("Authentication successful! You can now ssh into the client machine.")
    os_handler.print_platform_specific_notes(ssh_folder, key_type)

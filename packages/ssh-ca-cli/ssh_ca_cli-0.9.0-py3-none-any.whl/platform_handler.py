import hashlib
import os
import shutil
import subprocess
from typing import Union


class WindowsPlatformHandler:
    def __init__(self, app_dir_path):
        self.app_dir_path = app_dir_path

    def get_ssh_file_directory(self, ca_url: str, key_type):
        ca_url_hash = hashlib.sha256(ca_url.encode()).hexdigest()[:20]
        ssh_dir = self.app_dir_path / ca_url_hash
        shutil.rmtree(ssh_dir, ignore_errors=True)
        os.makedirs(ssh_dir)
        return ssh_dir

    def generate_key_files(self, key_type, ssh_dir):
        subprocess.run(
            [
                "ssh-keygen",
                "-t",
                key_type,
                "-f",
                f"{ssh_dir}/id_{key_type}",
                "-N",
                "",
            ]
        )

    @staticmethod
    def putty_pub_key(sign_response_text):
        # split certificate to lines of 64 each
        _, cert = sign_response_text.split(" ", maxsplit=1)
        n = 64
        return "\n".join(cert[i : i + n] for i in range(0, len(cert), n))

    def generate_cert_file_content(self, ssh_folder, key_type, sign_response_text):
        # powershell
        with open(f"{ssh_folder}/id_{key_type}-cert.pub", mode="w") as f:
            f.write(sign_response_text)

        # putty
        with open(f"{ssh_folder}/id_{key_type}-cert-putty.pub", mode="w") as f:
            cert_file_content = (
                "---- BEGIN SSH2 PUBLIC KEY ----\n" 'Comment: "SSH-CA"\n'
            )
            cert_file_content += f"{self.putty_pub_key(sign_response_text)}"
            cert_file_content += "---- END SSH2 PUBLIC KEY ----\n"
            f.write(cert_file_content)

    def prepare_ssh_agent(self, ssh_folder, key_type):
        # for powershell ssh
        os.system(f'ssh-add "{ssh_folder}/id_{key_type}"')

        # for putty
        # TODO: Make own implementation of this instead of relying on winscp
        os.system(
            f'winscp /keygen "{ssh_folder}/id_{key_type}" '
            f'/output="{ssh_folder}/id_{key_type}.ppk"'
        )

    def print_platform_specific_notes(self, ssh_folder, key_type):
        print("If you are using PuTTY, use the following files:")
        print(f"SSH Private Key (PPK Format): {ssh_folder}/id_{key_type}.ppk")
        print(
            f"SSH Certificate (Putty Format): {ssh_folder}/id_{key_type}-cert-putty.pub"
        )
        print("For powershell, just use the built in ssh command")


class UnixPlatformHandler:
    def __init__(self, app_dir_path):
        self.app_dir_path = app_dir_path

    def get_ssh_file_directory(self, ca_url: str, key_type):
        ca_url_hash = hashlib.sha256(ca_url.encode()).hexdigest()[:20]
        ssh_dir = self.app_dir_path / ca_url_hash
        if os.path.exists(f"{ssh_dir}/id_{key_type}.pub"):
            os.system(f"ssh-add -d '{ssh_dir}/id_{key_type}.pub' 2> /dev/null")
        if os.path.exists(f"{ssh_dir}/id_{key_type}-cert.pub"):
            os.system(f"ssh-add -d '{ssh_dir}/id_{key_type}-cert.pub' 2> /dev/null")
        shutil.rmtree(ssh_dir, ignore_errors=True)
        os.makedirs(ssh_dir)
        return ssh_dir

    def generate_key_files(self, key_type, ssh_dir):
        os.system(f"ssh-keygen -N '' -t {key_type} -f {ssh_dir}/id_{key_type}")

    def generate_cert_file_content(self, ssh_folder, key_type, sign_response_text):
        with open(f"{ssh_folder}/id_{key_type}-cert.pub", mode="w") as f:
            f.write(sign_response_text)

    def prepare_ssh_agent(self, ssh_folder, key_type):
        os.chmod(f"{ssh_folder}/id_{key_type}-cert.pub", 0o600)
        os.chmod(f"{ssh_folder}/id_{key_type}", 0o600)
        os.chmod(f"{ssh_folder}/id_{key_type}.pub", 0o600)
        os.system(f"ssh-add '{ssh_folder}/id_{key_type}' 2> /dev/null")

    def print_platform_specific_notes(self):
        pass


PlatformHandler = Union[
    WindowsPlatformHandler,
    UnixPlatformHandler,
]

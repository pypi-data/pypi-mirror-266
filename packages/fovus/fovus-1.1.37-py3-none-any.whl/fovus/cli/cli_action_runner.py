import json
import logging
import os
import shutil
import subprocess  # nosec
from datetime import datetime, timedelta
from http import HTTPStatus

import pkg_resources  # type: ignore
import requests
from packaging import version
from tqdm import tqdm

from fovus.adapter.fovus_api_adapter import FovusApiAdapter
from fovus.adapter.fovus_cognito_adapter import FovusCognitoAdapter
from fovus.adapter.fovus_s3_adapter import JOB_DATA_FILENAME, FovusS3Adapter
from fovus.adapter.fovus_sign_in_adapter import FovusSignInAdapter
from fovus.constants.cli_action_runner_constants import GENERIC_SUCCESS, OUTPUTS
from fovus.constants.cli_constants import (
    AUTO_DELETE_DAYS,
    CONFLICTING_CLI_ARGUMENT_SETS,
    CREATE_JOB_WITH_UPLOAD,
    DEBUG_MODE,
    DELETE_JOB,
    DOWNLOAD_JOB_FILES,
    EMPTY_FOLDER_LIST,
    FOVUS_PROVIDED_CONFIGS,
    GET_JOB_CURRENT_STATUS,
    JOB_CONFIG_FILE_PATH,
    JOB_FILE_ROOT_DIRECTORY,
    JOB_ID,
    JOB_ID_LIST,
    LOCAL_PATH,
    LOGIN,
    LOGOUT,
    MOUNT_STORAGE,
    OPEN_CONFIG_FOLDER,
    PATH_TO_CONFIG_FILE_IN_REPO,
    PATH_TO_CONFIG_FILE_LOCAL,
    PATH_TO_CONFIG_ROOT,
    PATH_TO_JOB_CONFIGS,
    PATH_TO_JOB_LOGS,
    PATH_TO_USER_CONFIGS,
    UNIX_OPEN,
    UNMOUNT_STORAGE,
    UPLOAD_FILES,
    USER,
    WINDOWS_DRIVE,
    WINDOWS_EXPLORER,
)
from fovus.constants.fovus_api_constants import ApiMethod
from fovus.exception.status_code_exception import StatusException
from fovus.exception.user_exception import UserException
from fovus.root_config import ROOT_DIR
from fovus.util.cli_action_runner_util import CliActionRunnerUtil
from fovus.util.file_util import FOVUS_JOB_INFO_FOLDER, FileUtil
from fovus.util.fovus_api_util import FovusApiUtil
from fovus.util.util import Util
from fovus.validator.fovus_api_validator import FovusApiValidator


class CliActionRunner:  # pylint: disable=too-few-public-methods
    def __init__(self, args_dict):
        self.args_dict = args_dict

    def run_actions(self):
        try:
            logging.info("CLI Arguments: %s", self.args_dict)
            self._confirm_latest_version()
            self._run_actions()
        except StatusException as exception:
            print(exception)

    def _run_actions(self):
        self._confirm_nonconflicting_argument_sets(CONFLICTING_CLI_ARGUMENT_SETS)

        if self.args_dict[OPEN_CONFIG_FOLDER]:
            self._confirm_required_arguments_present([])
            self._open_config_folder()

        if self.args_dict[LOGIN]:
            self._login()

        if self.args_dict[LOGOUT]:
            self._logout()

        if self.args_dict[USER]:
            self._user()

        if self.args_dict[CREATE_JOB_WITH_UPLOAD]:
            self._confirm_required_arguments_present([JOB_CONFIG_FILE_PATH, JOB_FILE_ROOT_DIRECTORY])
            self._confirm_forbidden_arguments_not_present([JOB_ID])
            self._create_job()

        if self.args_dict[MOUNT_STORAGE]:
            if Util.is_windows() or Util.is_unix():
                credentials_content = self._get_mount_storage_credentials()
                self._install_setup()
                self._mount_storage(credentials_content)
            else:
                print(f"Fovus mount storage is not available for your OS ({os.name}).")

        if self.args_dict[UNMOUNT_STORAGE]:
            if Util.is_windows() or Util.is_unix():
                self._unmount_storage()
            else:
                print(f"Fovus unmount storage is not available for your OS ({os.name}).")

        if self.args_dict[DOWNLOAD_JOB_FILES]:
            self._try_set_job_id()
            self._confirm_required_arguments_present([JOB_FILE_ROOT_DIRECTORY, JOB_ID])
            self._download_job_files()

        if self.args_dict[GET_JOB_CURRENT_STATUS]:
            self._try_set_job_id()
            self._confirm_required_arguments_present([JOB_ID])
            self._get_job_current_status()

        if self.args_dict[UPLOAD_FILES]:
            self._confirm_required_arguments_present([LOCAL_PATH])
            self._upload_file()

        if self.args_dict[DELETE_JOB]:
            self._confirm_required_arguments_present([JOB_ID, JOB_ID_LIST], require_all=False)
            self._delete_job()

    def _install_setup(self):
        commands = []
        previous_mount_storage_version = ""
        # https://github.com/awslabs/mountpoint-s3/releases
        current_mount_storage_version = "1.5.0"
        mount_storage_version_script_path = os.path.join(
            os.path.expanduser(PATH_TO_CONFIG_ROOT), "mount_storage.version"
        )
        if os.path.exists(mount_storage_version_script_path):
            with open(mount_storage_version_script_path, encoding="utf-8") as file:
                previous_mount_storage_version = file.read().strip()

        if Util.is_windows():
            version_result = subprocess.run(["wsl", "--version"], capture_output=True, text=True, check=False)  # nosec
            status_result = subprocess.run(["wsl", "--status"], capture_output=True, text=True, check=False)  # nosec
            if "WSL version" not in (
                "".join(filter(lambda x: x != "\x00", version_result.stdout)).split(":")
            ) or 'Enable "Virtual Machine Platform" by running: wsl.exe --install --no-distribution' in (
                "".join(filter(lambda x: x != "\x00", status_result.stdout)).split("\n")
            ):
                commands = [
                    (
                        "powershell Start-Process powershell -Verb runAs -ArgumentList "
                        "'-Command dism.exe /online /enable-feature /featurename:Microsoft-Windows-"
                        "Subsystem-Linux /all /norestart; Enable-WindowsOptionalFeature "
                        "-FeatureName VirtualMachinePlatform -Online -N ; wsl --update ; "
                        "wsl --set-default-version 2' -Wait"
                    )
                ] + commands

            result = subprocess.run(["wsl", "--list"], capture_output=True, text=True, check=False)  # nosec
            if "Fovus-Ubuntu" not in ("".join(filter(lambda x: x != "\x00", result.stdout)).split("\n")):
                print("Initializing setup for Fovus storage mount. It may take up to 5 minutes...")

                commands = commands + [
                    "wsl --set-default-version 2",
                    "curl -s -O https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64-root.tar.xz",
                    "wsl --import Fovus-Ubuntu . jammy-server-cloudimg-amd64-root.tar.xz --version 2",
                    "wsl -d Fovus-Ubuntu -u root -e rm jammy-server-cloudimg-amd64-root.tar.xz",
                ]
            else:
                print("Initializing setup for Fovus storage mount. It may take up to 2 minutes...")

            result = subprocess.run(
                "wsl -d Fovus-Ubuntu -u root -e mount-s3 --version", capture_output=True, text=True, check=False
            )  # nosec
            if ("mount-s3" not in ("".join(filter(lambda x: x != "\x00", result.stdout)).split(" "))) or (
                previous_mount_storage_version != current_mount_storage_version
            ):
                commands = commands + [
                    "wsl -d Fovus-Ubuntu -u root -e sudo apt-get update",
                    "wsl -d Fovus-Ubuntu -u root -e sudo apt-get upgrade -y",
                    "wsl -d Fovus-Ubuntu -u root -e sudo apt-get install -y awscli",
                    "wsl -d Fovus-Ubuntu -u root -e sudo apt-get install -y python3-pip",
                    "wsl -d Fovus-Ubuntu -u root -e sudo pip3 install fovus",
                    (
                        # https://s3.amazonaws.com/mountpoint-s3-release/latest/x86_64/mount-s3.deb
                        "wsl -d Fovus-Ubuntu -u root -e wget "
                        f"https://fovus-cli-dependencies.fovus.co/mount-storage/{current_mount_storage_version}/"
                        "ubuntu/mount-storage.deb"
                    ),
                    "wsl -d Fovus-Ubuntu -u root -e sudo apt-get install -y ./mount-storage.deb",
                    "wsl -d Fovus-Ubuntu -u root -e rm mount-storage.deb",
                ]

        elif Util.is_unix():
            print("Initializing setup for Fovus storage mount. It may take up to 2 minutes...")
            try:
                distribution = subprocess.check_output(["lsb_release", "-is"]).decode().strip().lower()  # nosec
            except subprocess.CalledProcessError as error:
                print("Error while checking linux distribution:", error)

            if previous_mount_storage_version != current_mount_storage_version:
                if distribution == "centos":
                    commands = [
                        "sudo yum upgrade -y",
                        "sudo yum install -y awscli",
                        "sudo yun install at",
                        "sudo service atd start",
                        # https://s3.amazonaws.com/mountpoint-s3-release/latest/x86_64/mount-s3.rpm
                        (
                            "wget -q https://fovus-cli-dependencies.fovus.co/mount-storage/"
                            f"{current_mount_storage_version}/centos/mount-storage.rpm"
                        ),
                        "sudo yum install -y ./mount-storage.rpm",
                        "rm mount-storage.rpm*",
                    ]
                elif distribution == "ubuntu":
                    commands = [
                        "sudo apt-get upgrade -y",
                        "sudo apt-get install -y awscli",
                        "sudo apt install at",
                        "sudo service atd start",
                        (
                            "wget -q https://fovus-cli-dependencies.fovus.co/mount-storage/"
                            f"{current_mount_storage_version}/ubuntu/mount-storage.deb"
                        ),
                        "sudo apt-get install -y ./mount-storage.deb",
                        "rm mount-storage.deb*",
                    ]

        if len(commands) > 0:
            total_iterations = len(commands)
            progress_bar = tqdm(total=total_iterations, desc="Setting up environments", unit="step")

            for command in commands:
                subprocess.run(
                    command, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True
                )  # nosec
                # process = subprocess.run(command, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # stdout, stderr = process.stdout.decode(), process.stderr.decode()
                # if stdout:
                #     print("STDOUT:", stdout)
                # if stderr:
                #     print("STDERR:", stderr)
                progress_bar.update(1)
            progress_bar.close()

            with open(mount_storage_version_script_path, "w", encoding="utf-8") as script_file:
                script_file.write(current_mount_storage_version)

        print(GENERIC_SUCCESS)

    def _get_mount_storage_credentials(self):
        fovus_api_adapter = FovusApiAdapter()
        user_id = fovus_api_adapter.get_user_id()
        workspace_id = fovus_api_adapter.get_workspace_id()

        mount_storage_credentials_body = fovus_api_adapter.get_mount_storage_credentials(
            FovusApiAdapter.get_mount_storage_credentials_request(user_id, workspace_id)
        )
        credentials_content = f"""
[default]
aws_access_key_id = {mount_storage_credentials_body["credentials"]["accessKeyId"]}
aws_secret_access_key = {mount_storage_credentials_body["credentials"]["secretAccessKey"]}
        """
        return credentials_content

    def _mount_storage(self, credentials_content):
        print("Mounting Fovus Storage...")
        fovus_api_adapter = FovusApiAdapter()
        user_id = fovus_api_adapter.get_user_id()
        workspace_id = fovus_api_adapter.get_workspace_id()

        mount_command = (
            f"mount-s3 fovus-{user_id}-{workspace_id}-us-east-1 /fovus-storage/files --prefix=files/ "
            "--allow-delete --file-mode=0770 --dir-mode=0770 > /dev/null 2>&1 && mount-s3 "
            f"fovus-{user_id}-{workspace_id}-us-east-1 /fovus-storage/jobs --prefix=jobs/ --allow-delete "
            "--file-mode=0550 --dir-mode=0550 > /dev/null 2>&1"
        )
        subprocess.run(  # nosec
            "fovus -us",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            shell=True,
        )

        for directory in ["~/.aws", "~/.fovus", "/fovus-storage/files", "/fovus-storage/jobs"]:
            if Util.is_windows():
                check_directory_command = [
                    "wsl",
                    "-d",
                    "Fovus-Ubuntu",
                    "-u",
                    "root",
                    "bash",
                    "-c",
                    f"[ -d {directory} ] && echo 'Exists' || echo 'Not Exists'",
                ]
                result = subprocess.run(check_directory_command, capture_output=True, text=True, check=False)  # nosec
                if result.stdout.strip() == "Not Exists":
                    create_directory_command = [
                        "wsl",
                        "-d",
                        "Fovus-Ubuntu",
                        "-u",
                        "root",
                        "bash",
                        "-c",
                        f"mkdir -p {directory}",
                    ]
                    subprocess.run(  # nosec
                        create_directory_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False
                    )
            elif Util.is_unix():
                if not os.path.exists(os.path.expanduser(f"{directory}")):
                    os.system(f"sudo mkdir -p {directory}")  # nosec
                    os.system(f"sudo chmod 777 {directory}")  # nosec

        if Util.is_windows():
            for file_name in [".credentials", ".device_information"]:
                with open(os.path.join(PATH_TO_CONFIG_ROOT, file_name), encoding="utf-8") as file:
                    fovus_credentials_content = file.read()
                subprocess.run(  # nosec
                    [
                        "wsl",
                        "-d",
                        "Fovus-Ubuntu",
                        "-u",
                        "root",
                        "bash",
                        "-c",
                        f"echo '{fovus_credentials_content.strip()}' > ~/.fovus/{file_name}",
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=False,
                )

            log_script_path = os.path.join(os.path.expanduser(PATH_TO_CONFIG_ROOT), "wsl_status.log")
            os.system(f"wsl --version > {log_script_path}")  # nosec
            os.system(f"wsl --status >> {log_script_path}")  # nosec
            os.system(f"wsl --list >> {log_script_path}")  # nosec

            subprocess.run(  # nosec
                [
                    "wsl",
                    "-d",
                    "Fovus-Ubuntu",
                    "-u",
                    "root",
                    "bash",
                    "-c",
                    f"echo '{credentials_content.strip()}' > ~/.aws/credentials",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            subprocess.run(  # nosec
                [
                    "wsl",
                    "-d",
                    "Fovus-Ubuntu",
                    "-u",
                    "root",
                    "bash",
                    "-c",
                    (f"echo '{mount_command}' > /etc/profile.d/fovus-storage-init.sh"),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )

            subprocess.run(  # nosec
                ["wsl", "-d", "Fovus-Ubuntu", "--shutdown"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )

            drive_name = self.args_dict.get(WINDOWS_DRIVE)
            mounted_drive_script_path = os.path.join(os.path.expanduser(PATH_TO_CONFIG_ROOT), "mount_storage.drive")
            if not drive_name:
                if os.path.exists(mounted_drive_script_path):
                    with open(mounted_drive_script_path, encoding="utf-8") as file:
                        drive_name = file.read().strip()
                else:
                    drive_name = "M"

            with open(mounted_drive_script_path, "w", encoding="utf-8") as script_file:
                script_file.write(drive_name)

            launch_wsl_script_content = rf"""Set shell = CreateObject("WScript.Shell")
            shell.Run "wsl -d Fovus-Ubuntu", 0
            Set FSO = CreateObject("Scripting.FileSystemObject")

            If FSO.DriveExists("{drive_name}:\") Then
                WScript.Echo "{drive_name}: drive is already mapped."
            Else
                shell.Run "cmd /c net use {drive_name}: \\wsl.localhost\Fovus-Ubuntu /persistent:yes", 0
                WScript.Echo "WSL directory mapped to {drive_name}: drive."
            End If
            """
            launch_wsl_script_path = os.path.join(os.path.expanduser(PATH_TO_CONFIG_ROOT), "launch_wsl.vbs")

            with open(launch_wsl_script_path, "w", encoding="utf-8") as script_file:
                script_file.write(launch_wsl_script_content)

            subprocess.run(  # nosec
                f'cscript "{launch_wsl_script_path}"',
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )

            # https://superuser.com/questions/263545/how-can-i-make-a-vb-script-execute-every-time-windows-starts-up
            fovus_path = os.path.expanduser(PATH_TO_CONFIG_ROOT)
            mount_fovus_storage_script_content = rf"""Set shell = CreateObject("WScript.Shell")
            shell.Run "cmd /k cd /D {fovus_path} && fovus -ms", 0"""
            startup_folder = os.path.join(
                os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
            )  # Use Win + R -> shell:startup
            mount_fovus_storage_script_path = os.path.join(startup_folder, "mount_fovus_storage.vbs")

            with open(mount_fovus_storage_script_path, "w", encoding="utf-8") as script_file:
                script_file.write(mount_fovus_storage_script_content)

            # Set scheduler to run the mount_fovus_storage.vbl after 28 days to refresh credentials
            future_date = datetime.now() + timedelta(days=28)
            formatted_date = future_date.strftime("%d/%m/%Y")
            command = rf"C:\Windows\System32\cscript.exe '{mount_fovus_storage_script_path}'"
            subprocess.run(  # nosec
                (
                    f'schtasks /create /tn "FovusMountStorageRefresh" /tr "{command}" /sc once '
                    f"/st 00:00 /sd {formatted_date} /f"
                ),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                shell=True,
            )

            print(
                rf"Your Fovus storage is successfully mounted under the path of {drive_name}:\fovus-storage\ as a "
                rf'network file system. The path to "My files" is {drive_name}:\fovus-storage\files, '
                rf'and the path to "Job files" is {drive_name}:\fovus-storage\jobs. Job files are read-only.'
                "\n\n"
                "The mounted network file system is optimized for high throughput read to large files by multiple "
                "clients in parallel and sequential write to new files by one client at a time subject to your network "
                "speed."
            )
            print(
                f"\033[91mA system reboot may be required. If you do not see a new {drive_name}:\\ drive gets mounted "
                'under "This PC", please reboot your system for it to take effect.\033[0m'
            )
        elif Util.is_unix():
            subprocess.run(  # nosec
                f"echo '{credentials_content.strip()}' > ~/.aws/credentials",
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True,
            )
            os.system("echo 'fovus -ms' | sudo tee  /etc/profile.d/fovus-storage-init.sh > /dev/null 2>&1")  # nosec
            #  https://www.redhat.com/sysadmin/linux-at-command
            os.system("atq | cut -f 1 | xargs atrm > /dev/null 2>&1")  # nosec
            os.system("echo 'fovus -ms' | at 00:00 + 28 day > /dev/null 2>&1")  # nosec
            os.system(mount_command)  # nosec
            print(
                "Your Fovus storage is successfully mounted under the path of /fovus-storage/ as a network "
                'file system (a system reboot may be needed). The path to "My files" is /fovus-storage/files, '
                'and the path to "Job files" is /fovus-storage/jobs. Job files are read-only.'
                "\n\n"
                "The mounted network file system is optimized for high throughput read to large files by multiple "
                "clients in parallel and sequential write to new files by one client at a time subject to your network "
                "speed."
            )

    def _unmount_storage(self):
        print("Unmounting Fovus Storage...")
        if Util.is_windows():
            drive_name = "M"
            mounted_drive_script_path = os.path.join(os.path.expanduser(PATH_TO_CONFIG_ROOT), "mount_storage.drive")
            if os.path.exists(mounted_drive_script_path):
                with open(mounted_drive_script_path, encoding="utf-8") as file:
                    drive_name = file.read().strip()

            current_dir = os.getcwd()
            if current_dir and current_dir.startswith(f"{drive_name}:"):
                print("Current directory:", current_dir)
                print(
                    f"Unmounting Fovus storage cannot be performed under {drive_name}:\\. "
                    f"This command must be issued from a path outside {drive_name}:\\. "
                )
                return

            for mount_dir in ["files", "jobs"]:
                result = subprocess.run(
                    [
                        "wsl",
                        "-d",
                        "Fovus-Ubuntu",
                        "-u",
                        "root",
                        "bash",
                        "-c",
                        (f"umount /fovus-storage/{mount_dir}"),
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                    shell=True,
                )  # nosec
                if result.stderr:
                    if "target is busy" in result.stderr.strip():
                        print("Mount point is busy!")
                        return

            subprocess.run(  # nosec
                [
                    "wsl",
                    "-d",
                    "Fovus-Ubuntu",
                    "-u",
                    "root",
                    "bash",
                    "-c",
                    ("sudo rm /etc/profile.d/fovus-storage-init.sh"),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )

            subprocess.run(  # nosec
                [
                    "wsl",
                    "-d",
                    "Fovus-Ubuntu",
                    "-u",
                    "root",
                    "bash",
                    "-c",
                    ("sudo rm ~/.aws/credentials"),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )

            subprocess.run(  # nosec
                ('schtasks /delete /tn "FovusMountStorageRefresh" /f'),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                shell=True,
            )

            launch_wsl_script_path = os.path.join(os.path.expanduser(PATH_TO_CONFIG_ROOT), "launch_wsl.vbs")
            subprocess.run(  # nosec
                f'del "{launch_wsl_script_path}"',
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                shell=True,
            )

            startup_folder = os.path.join(
                os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
            )  # Use Win + R -> shell:startup
            mount_fovus_storage_script_path = os.path.join(startup_folder, "mount_fovus_storage.vbs")
            subprocess.run(  # nosec
                f'del "{mount_fovus_storage_script_path}"',
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                shell=True,
            )

            subprocess.run(  # nosec
                f"net use {drive_name}: /delete /persistent:yes",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                shell=True,
            )
            subprocess.run(  # nosec
                f"powershell NET USE {drive_name}: /DELETE",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                shell=True,
            )
            print("Fovus storage successfully unmounted!")
        elif Util.is_unix():
            for mount_dir in ["files", "jobs"]:
                result = subprocess.run(
                    f"sudo umount /fovus-storage/{mount_dir}", capture_output=True, text=True, check=False, shell=True
                )  # nosec
                if result.stderr:
                    print(result.stderr.strip())
                    if "target is busy" in result.stderr.strip():
                        print("Mount point is busy!")
                    return
            os.system("atq | cut -f 1 | xargs atrm > /dev/null 2>&1")  # nosec
            os.system("sudo rm /etc/profile.d/fovus-storage-init.sh > /dev/null 2>&1")  # nosec
            os.system("sudo rm ~/.aws/credentials > /dev/null 2>&1")  # nosec
            print("Fovus storage successfully unmounted!")

    def _confirm_latest_version(self):
        try:
            response = requests.get("https://pypi.org/pypi/fovus/json", timeout=5)
            data = response.json()
            latest_version = data["info"]["version"]
        except (requests.RequestException, KeyError):
            print("Unable to check for latest version.")
            return

        try:
            current_version = pkg_resources.get_distribution("fovus").version
        except pkg_resources.DistributionNotFound:
            print("Unable to check for latest version.")
            return

        if version.parse(current_version) < version.parse(latest_version):
            print(
                "===================================================\n"
                + f"  A new version of Fovus CLI ({latest_version}) is available.\n"
                + f"  Your current version is {current_version}\n"
                + "  Update using: pip install --upgrade fovus\n"
                + "==================================================="
            )

    def _confirm_nonconflicting_argument_sets(self, conflicting_argument_sets):
        print("Confirming no conflicting arguments are present...")
        for conflicting_argument_set in conflicting_argument_sets:
            self._confirm_nonconflicting_arguments(conflicting_argument_set)
        print(GENERIC_SUCCESS)

    def _confirm_nonconflicting_arguments(self, conflicting_arguments):
        conflicting_arguments_count = 0
        for argument in self.args_dict.keys():
            if self.args_dict.get(argument) and argument in conflicting_arguments:
                conflicting_arguments_count += 1
        if conflicting_arguments_count > 1:
            raise UserException(
                HTTPStatus.BAD_REQUEST,
                self.__class__.__name__,
                "Only one of the following arguments can be used at a time: "
                + ", ".join(CliActionRunnerUtil.get_argument_string_list_from_keys(conflicting_arguments)),
            )

    def _confirm_required_arguments_present(self, argument_list, require_all=True):
        print("Confirming required arguments are present...")
        missing_arguments = []
        for argument in argument_list:
            if not self.args_dict.get(argument):
                missing_arguments.append(argument)
        if (len(missing_arguments) > 0 and require_all) or len(missing_arguments) == len(argument_list):
            raise UserException(
                HTTPStatus.BAD_REQUEST,
                self.__class__.__name__,
                f"{'Missing required arguments' if require_all else 'One of the following arguments is required'}: "
                + ", ".join(CliActionRunnerUtil.get_argument_string_list_from_keys(missing_arguments))
                + ".",
            )
        print(GENERIC_SUCCESS)

    def _confirm_forbidden_arguments_not_present(self, argument_list):
        print("Confirming forbidden arguments are not present...")
        forbidden_arguments = []
        for argument in argument_list:
            if self.args_dict.get(argument):
                forbidden_arguments.append(argument)
        if forbidden_arguments:
            raise UserException(
                HTTPStatus.BAD_REQUEST,
                self.__class__.__name__,
                "Forbidden arguments: "
                + ", ".join(CliActionRunnerUtil.get_argument_string_list_from_keys(forbidden_arguments))
                + ".",
            )
        print(GENERIC_SUCCESS)

    def _try_set_job_id(self):
        if self.args_dict.get(JOB_ID):
            return

        if self.args_dict.get(JOB_FILE_ROOT_DIRECTORY):
            print(
                "Job ID not specified. Attempting to find job ID in "
                + os.path.join(self.args_dict[JOB_FILE_ROOT_DIRECTORY], FOVUS_JOB_INFO_FOLDER, JOB_DATA_FILENAME)
                + "..."
            )
            job_data_file_path = os.path.join(
                self.args_dict[JOB_FILE_ROOT_DIRECTORY], FOVUS_JOB_INFO_FOLDER, JOB_DATA_FILENAME
            )
            if os.path.exists(job_data_file_path):
                with FileUtil.open(job_data_file_path) as file:
                    job_data = json.load(file)
                    self.args_dict[JOB_ID] = job_data.get(JOB_ID)
                    print("Job ID found: " + self.args_dict[JOB_ID])
                    return

        raise UserException(
            HTTPStatus.BAD_REQUEST,
            self.__class__.__name__,
            (
                "Missing job ID. This can be provided as an argument (via --job-id) or through the job data "
                "file (via --job-file-root-directory), which is automatically generated in the "
                "'job_root_folder/.fovus' directory when a job is created from the CLI."
            ),
        )

    def _open_config_folder(self):
        self._create_missing_directories()
        print(GENERIC_SUCCESS)
        self._create_missing_empty_config_files()
        print(GENERIC_SUCCESS)

        print("Opening config folder...")

        if Util.is_windows():
            subprocess.run(  # nosec
                [WINDOWS_EXPLORER, os.path.expanduser(PATH_TO_CONFIG_ROOT)], shell=False, check=False
            )
        elif Util.is_unix():
            subprocess.run([UNIX_OPEN, os.path.expanduser(PATH_TO_CONFIG_ROOT)], shell=False, check=False)  # nosec
        else:
            raise UserException(
                HTTPStatus.BAD_REQUEST,
                self.__class__.__name__,
                "Unsupported operating system. Only Windows and Unix are supported.",
            )
        print(GENERIC_SUCCESS)

    def _create_job(self):
        self._confirm_enable_debug_mode()
        self._confirm_set_auto_delete_days()
        print("Creating Fovus API adapter and Fovus S3 adapter and authenticating...")
        fovus_api_adapter = FovusApiAdapter()
        fovus_s3_adapter = FovusS3Adapter(fovus_api_adapter, self.args_dict, self.args_dict[JOB_FILE_ROOT_DIRECTORY])
        print(GENERIC_SUCCESS)

        user_id = fovus_api_adapter.get_user_id()
        workspace_id = fovus_api_adapter.get_workspace_id()

        print("Creating and validating create job request...")
        create_job_request = FovusApiAdapter.get_create_job_request(self.args_dict, user_id, workspace_id)
        fovus_api_adapter.make_dynamic_changes_to_create_job_request(create_job_request)
        validator = FovusApiValidator(create_job_request, ApiMethod.CREATE_JOB, self.args_dict[JOB_FILE_ROOT_DIRECTORY])
        validator.validate()
        print(GENERIC_SUCCESS)

        fovus_api_adapter.create_zombie_job_check_scheduler(
            {"jobId": FovusApiUtil.get_job_id(self.args_dict, user_id), "workspaceId": workspace_id}
        )
        empty_folderpath_list = fovus_s3_adapter.upload_files()
        create_job_request[EMPTY_FOLDER_LIST] = empty_folderpath_list

        print("Creating job...")
        fovus_api_adapter.create_job(create_job_request)
        print(GENERIC_SUCCESS)
        print(OUTPUTS)
        print(
            "\n".join(
                (
                    "Job name:",
                    create_job_request["jobName"],
                    "Job ID:",
                    FovusApiUtil.get_job_id(self.args_dict, user_id),
                )
            )
        )

    def _confirm_enable_debug_mode(self):
        if self.args_dict.get(DEBUG_MODE):
            print(
                "In debug mode, compute nodes will stay alive after each task execution until the task walltime is "
                + "reached to allow addtional time for debugging via SSH. Make sure to terminate your task or job "
                + "manually after debugging to avoid unnecessary charges for the additional time."
            )
            print("Are you sure you want to enable debug mode? (y/n):")
            if input() == "y":
                self.args_dict[DEBUG_MODE] = True
                print("Debug mode enabled")
            else:
                self.args_dict[DEBUG_MODE] = False
                print("Debug mode disabled")

    def _confirm_set_auto_delete_days(self):
        min_delete_days = 1
        max_delete_days = 1095  # 3 years
        if self.args_dict.get(AUTO_DELETE_DAYS):
            if not str(self.args_dict.get(AUTO_DELETE_DAYS)).isdigit() or not (
                int(self.args_dict.get(AUTO_DELETE_DAYS)) > min_delete_days
                and int(self.args_dict.get(AUTO_DELETE_DAYS)) < max_delete_days
            ):
                raise UserException(
                    HTTPStatus.BAD_REQUEST,
                    self.__class__.__name__,
                    f"Invalid scheduled delete days value of {self.args_dict.get(AUTO_DELETE_DAYS)} for "
                    + f"'{AUTO_DELETE_DAYS}'. Scheduled delete days value must be a positive number"
                    + f" and in a range of [{min_delete_days}, {max_delete_days}].",
                )
            print()
            if self._confirm_action(
                "This job will be submitted with an auto-delete timer that is set to"
                + f" {self.args_dict.get(AUTO_DELETE_DAYS)} days. The auto-delete timer starts"
                + " to tick upon job completion or termination. The job will be permanently "
                + "deleted when the timer expires.Are you sure you want to continue? (y/n):"
            ):
                print("Auto-delete is configured")
            else:
                self.args_dict[AUTO_DELETE_DAYS] = 0
                print("Auto-delete is not configured")

    def _confirm_action(self, message="Are you sure you want to continue? (y/n):") -> bool:
        print(message)
        return input() == "y"

    def _download_job_files(self):
        print("Authenticating...")
        fovus_api_adapter = FovusApiAdapter()
        fovus_s3_adapter = FovusS3Adapter(fovus_api_adapter, self.args_dict, self.args_dict[JOB_FILE_ROOT_DIRECTORY])
        fovus_s3_adapter.download_files()

    def _create_missing_directories(self):
        print("Creating missing config directories (if any)")
        for directory in (PATH_TO_CONFIG_ROOT, PATH_TO_JOB_CONFIGS, PATH_TO_USER_CONFIGS, PATH_TO_JOB_LOGS):
            if not os.path.exists(os.path.expanduser(directory)):
                os.makedirs(os.path.expanduser(directory), exist_ok=True)

    def _create_missing_empty_config_files(self):
        print("Creating missing empty config files (if any)")
        for config in FOVUS_PROVIDED_CONFIGS.values():
            empty_config_json_file_path = os.path.abspath(os.path.join(ROOT_DIR, config[PATH_TO_CONFIG_FILE_IN_REPO]))
            shutil.copy(empty_config_json_file_path, config[PATH_TO_CONFIG_FILE_LOCAL])

    def _get_job_current_status(self):
        print("Getting job current status...")
        fovus_api_adapter = FovusApiAdapter()
        job_current_status = fovus_api_adapter.get_job_current_status(self.args_dict[JOB_ID])
        print(GENERIC_SUCCESS)
        print(OUTPUTS)
        print("\n".join(("Job ID", self.args_dict[JOB_ID], "Job current status:", job_current_status)))

    def _upload_file(self):
        print("Authenticating...")
        fovus_api_adapter = FovusApiAdapter()
        fovus_s3_adapter = FovusS3Adapter(fovus_api_adapter, self.args_dict, self.args_dict[LOCAL_PATH])
        fovus_s3_adapter.upload_to_storage()

    def _login(self) -> None:
        fovus_sign_in_adapter = FovusSignInAdapter()
        fovus_sign_in_adapter.sign_in_concurrent()

    def _logout(self):
        print("Logging out...")

        FovusCognitoAdapter.sign_out()

        print(GENERIC_SUCCESS)

    def _user(self):
        fovus_api_adapter = FovusApiAdapter()
        fovus_api_adapter.print_user_info()

    def _delete_job(self):
        job_id_list = self.args_dict[JOB_ID_LIST] or []

        if self.args_dict[JOB_ID]:
            job_id_list.append(self.args_dict[JOB_ID])

        num_jobs = len(job_id_list)

        if not self._confirm_action(
            f"Are you sure you want to permanently delete {num_jobs} job{'' if num_jobs == 1 else 's'}? (y/n):"
        ):
            return

        print("Authenticating...")
        fovus_api_adapter = FovusApiAdapter()
        print("Deleting job...")
        fovus_api_adapter.delete_job(None, job_id_list)
        print(GENERIC_SUCCESS)

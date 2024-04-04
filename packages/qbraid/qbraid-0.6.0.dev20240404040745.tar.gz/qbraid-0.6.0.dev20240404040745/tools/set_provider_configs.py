# Copyright (C) 2023 qBraid
#
# This file is part of the qBraid-SDK
#
# The qBraid-SDK is free software released under the GNU General Public License v3
# or later. You can redistribute and/or modify it under the terms of the GPL v3.
# See the LICENSE file in the project root or <https://www.gnu.org/licenses/gpl-3.0.html>.
#
# THERE IS NO WARRANTY for the qBraid-SDK, as per Section 15 of the GPL v3.

"""
Unit tests related to setting, updating, and verifying
custom user configurations and required run-command pre-sets.

"""
import configparser
import os

from qbraid_core import QbraidSession
from qiskit_ibm_provider import IBMProvider

aws_cred_path = os.path.join(os.path.expanduser("~"), ".aws", "credentials")
aws_config_path = os.path.join(os.path.expanduser("~"), ".aws", "config")
qiskitrc_path = os.path.join(os.path.expanduser("~"), ".qiskit", "qiskitrc")
qbraidrc_path = os.path.join(os.path.expanduser("~"), ".qbraid", "qbraidrc")

# These environment variables don't actually exist in qBraid Lab, but instead
# are set and used for convenience for local development and testing.
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
ibmq_token = os.getenv("QISKIT_IBM_TOKEN")
qbraid_refresh_token = os.getenv("REFRESH")
qbraid_api_key = os.getenv("QBRAID_API_KEY")

# This is the only environment variable that actually exists in qBraid Lab
qbraid_user = os.getenv("JUPYTERHUB_USER")

# Skip tests if IBM/AWS account auth/creds not configured
skip_remote_tests: bool = os.getenv("QBRAID_RUN_REMOTE_TESTS", "False").lower() != "true"
REASON = "QBRAID_RUN_REMOTE_TESTS not set (requires configuration of qBraid storage)"

config_lst = [
    # (config_name, config_value, section, filepath)
    ["aws_access_key_id", aws_access_key_id, "default", aws_cred_path],
    ["aws_secret_access_key", aws_secret_access_key, "default", aws_cred_path],
    ["region", "us-east-1", "default", aws_config_path],
    ["output", "json", "default", aws_config_path],
    ["token", ibmq_token, "ibmq", qiskitrc_path],
    ["url", "https://auth.quantum-computing.ibm.com/api", "ibmq", qiskitrc_path],
    ["verify", "True", "ibmq", qiskitrc_path],
    ["default_provider", "ibm-q/open/main", "ibmq", qiskitrc_path],
]


def set_config():
    """Set config inside testing virtual environments with default values
    hard-coded and secret values read from environment variables.

    Note: this function is used for testing purposes only."""
    if skip_remote_tests:
        return

    IBMProvider.save_account(token=ibmq_token, overwrite=True)
    session = QbraidSession(
        user_email=qbraid_user, refresh_token=qbraid_refresh_token, api_key=qbraid_api_key
    )
    session.save_config()

    for file in [aws_config_path, aws_cred_path, qiskitrc_path]:
        try:
            os.remove(file)
        except FileNotFoundError:
            pass
    for c in config_lst:
        config_name = c[0]
        config_value = c[1]
        section = c[2]
        filepath = c[3]
        if not os.path.isfile(filepath):
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
        config = configparser.ConfigParser()
        config.read(filepath)
        if section not in config.sections():
            config.add_section(section)
        config.set(section, config_name, str(config_value))
        with open(filepath, "w", encoding="utf-8") as cfgfile:
            config.write(cfgfile)


if __name__ == "__main__":
    set_config()

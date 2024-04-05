import shutil
import os

from cgc.commands.auth import auth_utils
from cgc.utils.consts.env_consts import TMP_DIR, get_config_file_name
from cgc.utils.config_utils import get_config_path, save_to_config
from cgc.utils.message_utils import key_error_decorator_for_helpers


@key_error_decorator_for_helpers
def auth_register_response(response, user_id, priv_key_bytes, config_filename) -> str:
    TMP_DIR_PATH = os.path.join(get_config_path(), TMP_DIR)
    unzip_dir, namespace = auth_utils.save_and_unzip_file(response)
    aes_key, password = auth_utils.get_aes_key_and_password(unzip_dir, priv_key_bytes)

    os.environ["CONFIG_FILE_NAME"] = config_filename
    save_to_config(
        user_id=user_id, password=password, aes_key=aes_key, namespace=namespace
    )
    auth_utils.auth_create_api_key_with_save()
    shutil.rmtree(TMP_DIR_PATH)
    # config.json
    if config_filename == "config.json":
        return f"Register successful! You can now use the CLI. Saved data to:{os.path.join(get_config_path(),config_filename)}\n\
        Consider backup this file. It stores data accessible only to you with which you can access CGC platform."
    return f"New context created successfully! \nNew config file saved to: {os.path.join(get_config_path(),config_filename)}\n\
Consider backup this file. It stores data accessible only to you with which you can access CGC platform.\n \n\
Your user_id: {user_id}\n\
Your password: {password}\n\
To switch context use \ncgc context switch"


@key_error_decorator_for_helpers
def login_successful_response():
    return f"Successfully logged in, created new API key pair.\n\
                Saved data to: {os.path.join(get_config_path(), get_config_file_name())}.\n\
                Consider backup this file. It stores data accessible only to you with which you can access CGC platform."

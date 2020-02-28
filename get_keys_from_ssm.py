import boto3
import os

CURRENT_HOME = os.path.expanduser("~")
KEYS_DIR = os.path.join(CURRENT_HOME, ".keys")
PEM_KEY_NAME = os.getenv('PEM_KEY_NAME', 'jresendiz27-aws_exercises.pem')
SSM_PEM_KEY_NAME = os.getenv('SSM_PEM_KEY_NAME', 'jresendiz27_aws_exercises_pem')
SSM_VAULT_KEY_NAME = os.getenv('SSM_VAULT_KEY_NAME', 'vault_production')
VAULT_KEY_NAME = os.getenv('VAULT_KEY_NAME', '.vault-production')

'''
This function retrieves the information from SSM using the IAM keys 
and configures them in ~/.keys directory so ansible.cfg file can 
get them from the directory

Example:

```
PEM_KEY_NAME=name_for_pem_in_local.pem \
SSM_PEM_KEY_NAME=/route/to/ssm/pem/value \
SSM_VAULT_KEY_NAME=/route/to/ssm/vault \
VAULT_KEY_NAME=name_for_local_vault \
python get_keys_from_ssm.py
```

If the environment values are not provided, default values will be taken

'''


def sync_keys():
    print(KEYS_DIR)
    client = boto3.client('ssm')

    if not os.path.exists(f"{KEYS_DIR}"):
        print(f"Creating directory {KEYS_DIR}")
        os.makedirs(f"{KEYS_DIR}")
    print("Getting pem file from SSM")

    result = client.get_parameter(
        Name=SSM_PEM_KEY_NAME,
        WithDecryption=True
    )
    print("Writing pem to file")
    with open(f"{KEYS_DIR}/{PEM_KEY_NAME}", "+w") as file:
        file.write(result['Parameter']['Value'])
        file.close()

    print("Changing mode to pem file")
    os.chmod(f"{KEYS_DIR}/{PEM_KEY_NAME}", 400)

    print("Getting vault from SSM")

    vault = client.get_parameter(
        Name=SSM_VAULT_KEY_NAME,
        WithDecryption=True
    )

    print("Writing vault to file")
    with open(f"{KEYS_DIR}/{VAULT_KEY_NAME}", "+w") as file:
        file.write(vault['Parameter']['Value'])
        file.close()

    print("Done")


if __name__ == '__main__':
    sync_keys()

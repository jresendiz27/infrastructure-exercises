import boto3
import os

CURRENT_HOME = os.path.expanduser("~")
KEYS_DIR = os.path.join(CURRENT_HOME, ".keys")

'''
This function retrieves the information from SSM using the IAM keys 
and configures them in ~/.keys directory so ansible.cfg file can 
get them from the directory
'''


def sync_keys():
    print(KEYS_DIR)
    client = boto3.client('ssm')

    if not os.path.exists(f"{KEYS_DIR}"):
        print(f"Creating directoryf {KEYS_DIR}")
        os.makedirs(f"{KEYS_DIR}")
    print("Getting pem file from SSM")

    result = client.get_parameter(
        Name="jresendiz27_aws_exercises_pem",
        WithDecryption=True
    )
    print("Writing pem to file")
    with open(f"{KEYS_DIR}/jresendiz27-aws_exercises.pem", "+w") as file:
        file.write(result['Parameter']['Value'])
        file.close()

    print("Changing mode to pem file")
    os.chmod(f"{KEYS_DIR}/jresendiz27-aws_exercises.pem", 400)

    print("Getting vault from SSM")

    vault = client.get_parameter(
        Name="vault_production",
        WithDecryption=True
    )

    print("Writing vault to file")
    with open(f"{KEYS_DIR}/.vault-production", "+w") as file:
        file.write(vault['Parameter']['Value'])
        file.close()

    print("Done")


if __name__ == '__main__':
    sync_keys()

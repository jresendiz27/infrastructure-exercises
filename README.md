# Infrastructure examples
Examples of Infrastructure as Code and provisioning using terraform and ansible.

## Requirements

* Python 3+
+ Terraform 0.12+
+ Pipenv

## Preconfiguration

* Configure your AWS client (with your own credentials)
  * The credentials must be able to create resources and access to SSM parameter store
* If you already have keys and vault, change the [Ansible config](ansible.cfg) or override them via command line, check [Ansible Docs](https://docs.ansible.com/ansible/latest/cli/ansible-playbook.html) for further information 
* (Optional) If you're ssh key and vault values are (or are going to be) stored in SSM. Both must be ciphered. IAM credentials must have SSM access (GetParameters)
  * Check [Working with parameters](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-paramstore-working.html), for further information
* **All the examples must be executed inside the pipenv context**

Examples:

* [Nodejs Server with Systemd](systemd-node/Readme.md)
# Nodejs with Systemd 

The purpose of this exercise is to create a example server using Terraform and configure it a VPC, Internet Gateway, Security Groups, etc. And provision the instance with Node js (Via apt or NVM), install it and check it's working.
Setup a systemd daemon to handle the process. Secrets management also handled by ansible-vault.

## IaC
### How to run it?
Inside `systemd-node` folder:
`terraform init`
`terraform plan -out=systemd_node_tf`
`terraform apply systemd_node_tf`
This will create the infrastructure in AWS and keep everything configured.

> Don't forget to change the key in the [vars](vars.tf) file, so you can have access to the instance via ssh.

## Provisioning 
### How to run it?

* Update the [hosts](../hosts) file with the DNS or IP provided by AWS or using `terraform show`
  * You can also pass the hosts via CLI, check [Ansible Docs](https://docs.ansible.com/ansible/latest/cli/ansible-playbook.html)
* Inside the root folder of the project run the next command:
  * `ansible-playbook -i hosts systemd-node/playbook.yml --tags install_node`
  * The `--tags` executes the tags related in the playbook/roles.
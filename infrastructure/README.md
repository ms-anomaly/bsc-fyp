# Infrastructure

Define the following variable in the `terraform.tfvars` file.
```
# Authentication
aws_profile  = "yourAWSprofile"

# Resource
instance_name = "Robot-Shop"
```
You should add your AWS profile details in the `~/.aws/tf_user/conf` 
and `~/.aws/tf_user/creds` files.

`conf`
```
[profile yourAWSprofile]
region = "yourAWSprofile ap-southeast-1"
```

`creds`
```
[yourAWSprofile]
aws_access_key_id="yourAWSprofile access key"
aws_secret_access_key="yourAWSprofile secret key"
aws_session_token=
```

Install the provider pluging
```
terraform init
```

Deploy the infrastructure
```
terraform apply
```

Destroy the infrastructure
```
terraform destroy
```

# dmwrapcli

A simple docker-machine wrapper.  Specify docker-machine line args in a .yml 
file.

## using dmwrapcli

```
    $ python3 dmwrap.py -h
      usage:
          dmwrap.py create [options] <machine-name>
          
          
      options:
          --driver DRIVER    [default: amazonec2]
          --amazonec2-access-key AWS_ACCESS_KEY_ID
          --amazonec2-secret-key AWS_SECRET_ACCESS_KEY
          --amazonec2-session-token AWS_SESSION_TOKEN
          --amazonec2-ami AWS_AMI
          --amazonec2-region AWS_DEFAULT_REGION
          --amazonec2-vpc-id AWS_VPC_ID
          --amazonec2-zone AWS_ZONE
          --amazonec2-subnet-id AWS_SUBNET_ID
          --amazonec2-security-group AWS_SECURITY_GROUP
          --amazonec2-tags AWS_TAGS
          --amazonec2-instance-type AWS_INSTANCE_TYPE
          --amazonec2-device-name AWS_DEVICE_NAME
          --amazonec2-root-size AWS_ROOT_SIZE
          --amazonec2-volume-type AWS_VOLUME_TYPE
          --amazonec2-iam-instance-profile AWS_INSTANCE_PROFILE
          --amazonec2-ssh-user AWS_SSH_USER
          --amazonec2-request-spot-instance
          --amazonec2-spot-price
          --amazonec2-use-private-address
          --amazonec2-private-address-only
          --amazonec2-monitoring
          --amazonec2-use-ebs-optimized-instance
          --amazonec2-ssh-keypath AWS_SSH_KEYPATH	
          --amazonec2-retries
          --userconfig USERCONFIG        path to user config file with above options 
                                         in yml format.
```

passing a userconfig file

```
    python2 dmwrap.py create --userconfig defaults.yml my_new_ec2
```

format of defaults.yml:

```
    --amazonec2-access-key: None
    --amazonec2-secret-key: None
    --amazonec2-session-token: None
    --amazonec2-ami: None
    --amazonec2-region: None
    --amazonec2-vpc-id: None
    --amazonec2-zone: None
    --amazonec2-subnet-id:
    --amazonec2-security-group: None
    --amazonec2-tags: None
    --amazonec2-instance-type: None
    --amazonec2-device-name: None
    --amazonec2-root-size: None
    --amazonec2-volume-type: None
    --amazonec2-iam-instance-profile: None
    --amazonec2-ssh-user: None
    --amazonec2-request-spot-instance: None
    --amazonec2-spot-price: None
    --amazonec2-use-private-address: None
    --amazonec2-private-address-only: None
    --amazonec2-monitoring: None
    --amazonec2-use-ebs-optimized-instance: None
    --amazonec2-ssh-keypath: None
    --amazonec2-retries: None
```         

__author__ = 'Sean Landry'
__date__ = '20june2017'
__version__ = '0.1.0'

"""
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

"""

import subprocess
from docopt import docopt
import yaml
import os

def parse_opts(opts = None):
    optlst = []
    if opts['--userconfig']:
        userconfig = os.path.abspath(opts['--userconfig'])
        print(userconfig)
        with open(userconfig, 'r') as user:
            config = yaml.load(user)
            for k,v in config.items():
                if v != 'None' and ('amazon' in k or 'driver' in k):
                    optlst.append(k)
                    optlst.append(v)

    for k,v in opts.items():
        if k not in optlst and '--' in k and v and ('amazon' in k or 'driver' in k):
            optlst.append(k)
            optlst.append(v)
    return optlst

if __name__== "__main__":
    """
    Command line arguments.
    """
    options = docopt(__doc__)
    
    if options['create']:
        opts = parse_opts(options)
        args = ["docker-machine", "create"] + opts + [options['<machine-name>']]
        subprocess.run(args)

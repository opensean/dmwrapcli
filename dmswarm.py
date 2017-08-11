#!/usr/bin/env python3

## TO DO
##     - add support for additional cloud provider drivers 
##     - add option to scp copy directories or files to the manager such
##       as aws credentials

"""
Quickly launch a docker swarm on AWS.

Important
docker-machine creates a default security group that does not have all of 
the require ports open for docker swarm.  An aws security group with the
following configuration was tested and worked.

Inbound
Type              Protocol  Port Range     Source
Custom TCP Rule   TCP       2377           0.0.0.0/0
SSH               TCP       22             0.0.0.0/0
Custom UDP Rule   UDP       7946           0.0.0.0/0
Custom TCP Rule   TCP       2376           0.0.0.0/0
Custom TCP Rule   TCP       7946           0.0.0.0/0
Custom UDP Rule   UDP       4789           0.0.0.0/0

Outbound
Type              Protocol  Port Range     Source
All traffic       All       All            0.0.0.0/0

Currently, this program does not have the ability to change an existing 
security group.  One can specify a security group with above configuration 
using the '--amazonec2-security-group AWS_SECURITY_GROUP' arg or create 
(or modify) a security group named 'docker-machine'.  docker-machine will
create a security group named 'docker-machine' or use an existing group 
named 'docker-machine' if the '--amazonec2-security-group AWS_SECURITY_GROUP' 
arg is omitted.


usage:
    dmwswarm.py create [options] <swarm-name>
    
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
   
    --log-level LOG             Set the log level to DEBUG, INFO, WARNING, 
                                CRITICAL, or ERROR [default: DEBUG].

    --nodes NODES               Number of worker nodes.

    --userconfig USERCONFIG     Path to user config file with above options 
                                in yml format.

"""
__author__ = 'Sean Landry'
__date__ = '24july2017'
__version__ = '0.1.0'


import subprocess
from docopt import docopt
import json
import yaml
import os
import logging
import sys

class DMSubprocess():
    """
    Serves as the base class for all docker-machine subprocess calls.

    """

    def __init__(self, log_level = "INFO", action = None, optDict = None, 
                 machine_name = None, sshArgs = None):
        """
        Construct a DMSubprocess object.
        
        Args:
        log_level (str): set the logging level to DEBUG, INFO, WARNING, 
                         CRITICAL, or ERROR.

        optDict (dict): a dictionary of options to be passed to the 
                        docker-machine subprocess call.
        
        action (str): the main docker-machine arg, e.g. create
        
        """
        self.logger = self.init_logger(log_level)
        self.options = self.parse_opts(optDict)
        self.machine_name = machine_name
        self.action = action
        self.sshArgs = sshArgs
        self.stdout = ''
        self.stderr = ''
        self.argLst = self.dm_action(action)

    def init_logger(self, log_level = "WARNING"):
        """
        Initialize the class logger.

        Args:
            log_level (str): set logging level to DEBUG, INFO, WARNING, 
                             CRITICAL, or ERROR.
        
        Returns:
            class_logger (logging obj): python logging object with class name.
        """

        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % log_level)
        
        class_logger = logging.getLogger(self.__class__.__name__)
        class_logger.setLevel(numeric_level)

        class_logger.debug('logger initialized')
        return class_logger

    def dm_action(self, action):
        all_actions = {
            'ssh':["docker-machine", action, self.machine_name, self.sshArgs],
            'create':["docker-machine"] + [action] + self.options + [self.machine_name],
            'inspect':["docker-machine", action, self.machine_name]
            }
        
        return all_actions[action]

    def parse_opts(self, opts = None):
        optlst = []
        if opts['--userconfig']:
            userconfig = os.path.abspath(opts['--userconfig'])
            print(userconfig)
            with open(userconfig, 'r') as user:
                config = yaml.load(user)
                for k,v in config.items():
                    if v != 'None' and (opts['--driver'] in k or 'driver' in k):
                        optlst.append(k)
                        optlst.append(v)
    
        for k,v in opts.items():
            if k not in optlst and '--' in k and v and (opts['--driver'] in k or 'driver' in k):
                optlst.append(k)
                optlst.append(v)

        self.logger.debug("parse_opts --> " + str(optlst))
        return optlst

    def private_ip(self, stdout):
        result = json.loads(stdout.decode())
        return result['Driver']['PrivateIPAddress'] 

    def parse_token(self, stdout):
        for line in stdout.decode().split('\n'):
            if 'docker swarm join --token' in line:
                return line.strip()

    def log_streams(self, stdout = False, stderr = True):
        self.logger.info("finished subprocess, stream logs:")
        if stdout and self.stdout:
            self.logger.info("stdout: \n" + self.stdout.decode())
        if stderr and self.stderr:
            self.logger.info("stderr: \n" + self.stderr.decode())

    def run(self, proc_in = None):
        """
        Run the subprocess.

        Args:
            proc_in (boolean):         Set to True of subprocess call will be 
                                       expecting the stdout PIPE of another 
                                       subprocess call.

        """
        
        self.logger.info("running subprocess")
        self.logger.info("using args --> " + str(self.argLst))

        if proc_in:
            proc = subprocess.Popen(self.argLst, stdout = subprocess.PIPE,
                                    stderr = subprocess.PIPE,
                                    stdin = subprocess.PIPE)
            self.stdout, self.stderr = proc.communicate(input = proc_in)

        else:
            proc = subprocess.Popen(self.argLst, stdout = subprocess.PIPE,
                                    stderr = subprocess.PIPE)

            self.stdout,self.stderr = proc.communicate()



def main():
    """
    Command line arguments.
    """
    options = docopt(__doc__)
    
    log_level = options['--log-level']
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level)


    ## setup module logger
    moduleLogger = logging.getLogger()
    moduleLogger.setLevel(numeric_level)

    # create console handler
    console = logging.StreamHandler()
    console.setLevel(numeric_level)

    # create formatter and add it to the handler
    console_formatter = logging.Formatter('%(asctime)s %(filename)s %(name)s.%(funcName)s() - %(levelname)s:%(message)s')
    console.setFormatter(console_formatter)

    moduleLogger.addHandler(console)
    
    if options['create']:
        
        ## launch the swarm nodes
        if options['--nodes']:
            for n in range(int(options['--nodes'])):
                if n == 0:
                    moduleLogger.info("creating " + options['<swarm-name>'] + "-manager")
                    node = DMSubprocess(
                                action = 'create',
                                optDict = options, 
                                machine_name = options['<swarm-name>'] +"-manager",
                                log_level = log_level)

                else:
                    moduleLogger.info("creating " + options['<swarm-name>'] + "-worker-" 
                                      + str(n))

                    node = DMSubprocess(
                                 action = 'create',
                                 optDict = options,
                                 machine_name = options['<swarm-name>'] +"-worker-" + str(n),
                                 log_level = log_level)

                node.run()
                node.log_streams(stdout = True)
        


        ## inspect manager node to obtain ip
        moduleLogger.info('finding manager ip')

        manager = DMSubprocess(
                           action = 'inspect',
                           optDict = options,
                           log_level = log_level, 
                           machine_name = options['<swarm-name>'] + "-manager")
        
        manager.run()
        manager.log_streams(stdout = True)
        ip = manager.private_ip(manager.stdout)
     
        moduleLogger.debug("manager private ip " + ip)


        ## initialize manager node
        moduleLogger.info('initializing swarm manager')

        manager = DMSubprocess(
                       action = 'ssh',
                       optDict = options,
                       log_level = log_level, 
                       machine_name = options['<swarm-name>'] + "-manager", 
                       sshArgs = "sudo docker swarm init --advertise-addr " + ip)

        manager.run()
        manager.log_streams(stdout = True) 
        token = manager.parse_token(manager.stdout)
        moduleLogger.debug(token)

        ## add workers to the swarm
        for n in range(int(options['--nodes']) - 1):
            moduleLogger.info(options['<swarm-name>'] + "-worker-" + str(n+1) 
                              + " is attempting to join the swarm")
       
            moduleLogger.debug(token)
            
            worker = DMSubprocess(
                          action = 'ssh',
                          optDict = options,
                          log_level = log_level,
                          machine_name = options['<swarm-name>'] + "-worker-" 
                                                 + str(n+1),
                          sshArgs = "sudo " + token)
            worker.run()
            worker.log_streams(stdout = True)

if __name__== "__main__":
    
    main()

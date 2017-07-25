#!/usr/bin/env python3
"""
THIS MODULE IS A WORK IN PROGRESS AND IS NOT FULLY FUNCTIONAL.

STATUS
- all nodes launch sucessfully
- manager node is intialized successfully
- worker nodes are unable to join swarm
    - need to include --advertise-addr arg when initializing the manager?

Quickly launch a docker swarm on AWS.

usage:
    dmwswarm.py create [options] <machine-name>...
    
    
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

    --node-count NODE           Number of worker nodes.

    --userconfig USERCONFIG     Path to user config file with above options 
                                in yml format.

"""
__author__ = 'Sean Landry'
__date__ = '24july2017'
__version__ = '0.1.0'


import subprocess
from docopt import docopt
import yaml
import os
import logging
import sys

class DMSubprocessBase():
    """
    Serves as the base class for all docker-machine subprocess calls.

    """

    def __init__(self, log_level = "WARNING", dmArg = None, optDict = None, 
                 machine_name = None):
        """
        Construct a DMSubprocessBase object.
        
        Args:
        log_level (str): set the logging level to DEBUG, INFO, WARNING, 
                         CRITICAL, or ERROR.

        optDict (dict): a dictionary of options to be passed to the 
                        docker-machine subprocess call.
        
        dmArg (str): the main docker-machine arg, e.g. create
        
        """
        self.logger = self.init_logger(log_level)
        self.options = optDict
        self.argLst = ["docker-machine"] + [dmArg] + self.options + [self.machine_name]

    def init_logger(self, log_level = "WARNING"):
        """
        Initialize the class logger.

        This method will change the root logger level if not equal to the 
        log_level arg, which is necessary if working with this class in 
        an ipython session. The logging library uses a hierarchy structure 
        meaning child loggers will pass args to parent first, the root 
        loggers default level is 30 (logging.WARNING).  Therefore, need to 
        set root logger to log arg level to allow child logger a chance to 
        handle logging output

        Args:
            log_level (str): set logging level to DEBUG, INFO, WARNING, 
                             CRITICAL, or ERROR.
        
        Returns:
            class_logger (logging obj): python logging object with class name.
        """

        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % log_level)
        rootLogger = logging.getLogger()
        class_logger = logging.getLogger(self.__class__.__name__)

        ## change root logger level if not equal to log arg 
        if rootLogger.level != numeric_level:
            logging.basicConfig(level = numeric_level)

        class_logger.debug('logger initialized')
        return class_logger

    def run(self, proc_in = False, proc_out = False):
        """
        Run the subprocess.

        Args:
            proc_in (boolean): Set to True of subprocess call will be 
                               expecting the stdout PIPE of another 
                               subprocess call.

            proc_out (boolean): if proc_out is set to True return the 
                                subprocess object.  If proc_out is set 
                                to False the stdout and stderr are 
                                sent to the class logger.

        Returns:
            proc (subprocess obj): if proc_out is set to True return the 
                                   subprocess object.  If proc_out is set 
                                   to False the stdout and stderr are 
                                   sent to the class logger.
        """
        self.logger.info("running subprocess")
        self.logger.debug("using args --> " + str(self.argLst))
        if proc_in:
            proc = subprocess.Popen(self.argLst, stdout = subprocess.PIPE,
                                    stderr = subprocess.STDOUT,
                                    stdin = subprocess.PIPE)
        else:
            proc = subprocess.Popen(self.argLst, stdout = subprocess.PIPE,
                                    stderr = subprocess.STDOUT)

        if not proc_out:
            for line in proc.stdout:
                self.logger.info(line.decode().strip())
        else:
            return proc


class DMCreateSubprocess(DMSubprocessBase):

    def __init__(self, log_level = "WARNING", dmArg = 'create', optDict = None, 
                 machine_name = None):
        """
        Construct a DMCreateSubprocess object.

        Args:
            log_level (str): set the logging level to DEBUG, INFO, WARNING, 
                             CRITICAL, or ERROR.

            optDict (dict): a dictionary of options to be passed to the 
                            docker-machine subprocess call.
            
            dmArg (str): the main docker-machine arg, e.g. create
        """
        self.logger = self.init_logger(log_level)
        self.machine_name = machine_name
        self.options = self.parse_opts(opts = optDict)
        self.argLst = ["docker-machine"] + [dmArg] + self.options + [self.machine_name]

    def parse_opts(self, opts = None):
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


class DMSshSubprocess(DMSubprocessBase):

    def __init__(self, log_level = "WARNING", dmArg = 'ssh', sshArgs = None, machine_name = None):
        """
        Construct a DMCreateSubprocess object.

        Args:
            log_level (str): set the logging level to DEBUG, INFO, WARNING,
                             CRITICAL, or ERROR.

            dmArg (str): the main docker-machine arg, e.g. create
        """
        self.logger = self.init_logger(log_level)
        self.machine_name = machine_name
        self.argLst = ["docker-machine", dmArg, self.machine_name, sshArgs]

    def parse_token(self, stdout):
        for line in stdout.decode().split('\n'):
            if 'docker swarm join --token' in line:
                return line.strip()

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
        if options['--node-count']:
            for n in range(int(options['--node-count'])):
                moduleLogger.info("creating " + options['<machine-name>'][n])
                node = DMCreateSubprocess(optDict = options, 
                                        machine_name = options['<machine-name>'][n],
                                        log_level = log_level)
                node.run()

        ## initialize manager node
        moduleLogger.info('initializing swarm manager')

        ## need to include --advertise-addr
        ## use docker-machine inspect machine to retrieve PrivateIp address
        ## and advertise it
        manager = DMSshSubprocess(log_level = log_level, 
                                  machine_name = options['<machine-name>'][0], 
                                  sshArgs = "sudo docker swarm init")
        man_proc = manager.run(proc_out = True)
        stdout, stderr = man_proc.communicate()
        
        token = manager.parse_token(stdout)
        moduleLogger.debug(token)

        ## add workers to the swarm
        for n in range(int(options['--node-count']) - 1):
            moduleLogger.info(options['<machine-name>'][n+1] 
                              + " is attempting to join the swarm")
       
            worker = DMSshSubprocess(log_level = log_level,
                                  machine_name = options['<machine-name>'][n +1],
                                  sshArgs = "sudo " + token)
            worker.run()
            
            moduleLogger.debug(token)
            moduleLogger.info(options['<machine-name>'][n +1] 
                              + " successfully joined the swarm.")

if __name__== "__main__":
    
    main()

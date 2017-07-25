#!/usr/bin/env python3
"""
THIS MODULE IS A WORK IN PROGRESS AND NOT FUNCTIONAL.

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

    def __init__(self, log_level = "WARNING", argDict = None, 
                 machine_name = None):
        """
        Construct a DMSubprocessBase object.

        Args:
        log_level (str): set the logging level to DEBUG, INFO, WARNING, 
                         CRITICAL, or ERROR.

        argDict (dict): a dictionary of options to be passed to the 
                        docker-machine subprocess call.
        
        """
        self.logger = self.init_logger(log_level)
        self.args = argDict
        self.machine_name = machine_name
        self.options = self.parse_opts(opts = argDict)
        self.argLst = ["docker-machine", "create"] + self.options + [self.machine_name]

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
        self.logger.info("using args --> " + str(self.argLst))
        if proc_in:
            proc = subprocess.Popen(self.argLst, stdout = subprocess.PIPE,
                                    stderr = subprocess.PIPE,
                                    stdin = subprocess.PIPE)
        else:
            proc = subprocess.Popen(self.argLst, stdout = subprocess.PIPE,
                                    stderr = subprocess.PIPE)

        if not proc_out:
            proc_pipe = proc.communicate()
            self.logger.info("finished subprocess")
            self.logger.info("stdout: \n" + proc_pipe[0].decode())
            self.logger.info("stderr: \n" + proc_pipe[1].decode())
        else:
            return proc


def main():
    """
    Command line arguments.
    """
    options = docopt(__doc__)
    
    if options['create']:

        ## launch the swarm manager
        manager = DMSubprocessBase(argDict = options, machine_name = options['<machine-name>'][0])
        sys.stderr.write(manager.machine_name + '\n')
        manager.run()

        
        ## launch the worker nodes
        if options['--node-count']:
            c = 1
            for n in range(int(options['--node-count'])):
                node = DMSubprocessBase(argDict = options, machine_name = options['<machine-name>'][c])
                sys.stderr.write(node.machine_name + '\n')
                node.run()
                c += 1



if __name__== "__main__":
    
    main()

#!/usr/bin/env python

import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../AppDB'))
from cassandra_env import cassandra_interface

sys.path.append(os.path.join(os.path.dirname(__file__), '../lib'))
from constants import APPSCALE_HOME
from zkappscale import zktransaction as zk
import monit_app_configuration
import monit_interface

import datastore_upgrade

# The location of the Cassandra binary on the local filesystem.
CASSANDRA_EXECUTABLE = cassandra_interface.CASSANDRA_INSTALL_DIR \
  + "/cassandra/bin/cassandra"

# The location on the local file system where we write the process ID
# that Cassandra runs on.
PID_FILE = "/var/appscale/appscale-cassandra.pid"

# The default port to connect to Cassandra.
CASSANDRA_PORT = 9999

def start_service(service_name):
  logging.info("Starting " + service_name)
  watch_name = ""
  if service_name == "cassandra":
    start_cmd = CASSANDRA_EXECUTABLE + " start -p " + PID_FILE
    stop_cmd = "/usr/bin/python2 " + APPSCALE_HOME + "/scripts/stop_service.py java cassandra"
    watch_name = datastore_upgrade.CASSANDRA_WATCH_NAME
    ports = [CASSANDRA_PORT]
    match_cmd = cassandra_interface.CASSANDRA_INSTALL_DIR

  if service_name == "zookeeper":
    start_cmd = "/usr/sbin/service " + "zookeeper" + " start"
    stop_cmd = "/usr/sbin/service " + "zookeeper" + " stop"
    watch_name = datastore_upgrade.ZK_WATCH_NAME
    match_cmd = "org.apache.zookeeper.server.quorum.QuorumPeerMain"
    ports = [zk.DEFAULT_PORT]

  monit_app_configuration.create_config_file(watch_name, start_cmd, stop_cmd,
    ports, upgrade_flag=True, match_cmd=match_cmd)

  if not monit_interface.start(watch_name):
    logging.error("Monit was unable to start " + service_name)
    return 1
  else:
    logging.info("Successfully started " + service_name)
    return 0

if __name__ == "__main__":
  args_length = len(sys.argv)
  if args_length < 2:
    sys.exit(1)

  service_name = (str(sys.argv[1]))
  start_service(service_name)

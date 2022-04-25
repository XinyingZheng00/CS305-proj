#!/usr/bin/env python

import sys

import os
import time
import logging
import argparse
from util import check_output, check_both, run_bg, strip_comments
from apache_setup import configure_apache, reset_apache, restart_apache, is_apache_configured
import socket

BUF_SIZE = 8192

APACHE_SERVER_PORT = [8080, 8081]
LINK_PORT = [15641, 15640]
INITIAL_BANDWIDTH_BIT_PER_SEC = 128000
CONTROL_PORT = 7777

servers = []
servers_port = []

ONELINK_TEMPLATE = '''
ms :: MultiSocket(127.0.0.1, %d, 127.0.0.1, %d)
    -> Queue(10000)
    -> link_1 :: BandwidthRatedUnqueue(%d, BURST_BYTES 250)
    -> ms

ControlSocket("TCP", %d);
'''

TWOLINK_TEMPLATE = '''
ms_1 :: MultiSocket(127.0.0.1, %d, 127.0.0.1, %d)
    -> Queue(10000)
    -> link_1 :: BandwidthRatedUnqueue(%d, BURST_BYTES 250)
    -> ms_1

ms_2 :: MultiSocket(127.0.0.1, %d, 127.0.0.1, %d)
    -> Queue(10000)
    -> link_2 :: BandwidthRatedUnqueue(%d, BURST_BYTES 250)
    -> ms_2

ControlSocket("TCP", %d);
'''

SHARELINK_TEMPLATE = '''
ms_1 :: MultiSocket(127.0.0.1, %d, 127.0.0.1, %d)
    -> Queue(10000)
    -> Unstrip(2)
    -> StoreData(0, 00)
    -> [0]switch :: SimpleRoundRobinSched();


ms_2 :: MultiSocket(127.0.0.1, %d, 127.0.0.1, %d)
    -> Queue(10000)
    -> Unstrip(2)
    -> StoreData(0, 01)
    -> [1]switch;

switch -> link_1 :: BandwidthRatedUnqueue(%d, BURST_BYTES 250)
    -> classifier :: Classifier(0/3030, -)

classifier[0] -> Strip(2) -> ms_1
classifier[1] -> Strip(2) -> ms_2

ControlSocket("TCP", %d);
'''


def is_click_running():
    return 'click' in check_both('ps -e | grep click | grep -v grep'\
        , shouldPrint=False, check=False)[0][0]

def servers_running():
    return is_apache_configured()\
        or is_click_running()

def autogen_click():
    click_conf = args.topology + '.click'

    # Remove existing log file
    if os.path.isfile(click_conf):
        os.remove(click_conf)

    with open(click_conf, 'w') as click_conf_file:
        if args.topology == 'onelink':
            click_conf_file.write(ONELINK_TEMPLATE % (LINK_PORT[0], APACHE_SERVER_PORT[0], INITIAL_BANDWIDTH_BIT_PER_SEC, CONTROL_PORT))
        if args.topology == 'twolink':
            click_conf_file.write(TWOLINK_TEMPLATE % (LINK_PORT[0], APACHE_SERVER_PORT[0], INITIAL_BANDWIDTH_BIT_PER_SEC, 
                                                      LINK_PORT[1], APACHE_SERVER_PORT[1], INITIAL_BANDWIDTH_BIT_PER_SEC, CONTROL_PORT))
        if args.topology == 'sharelink':
            click_conf_file.write(SHARELINK_TEMPLATE % (LINK_PORT[0], APACHE_SERVER_PORT[0], 
                                                        LINK_PORT[1], APACHE_SERVER_PORT[1], INITIAL_BANDWIDTH_BIT_PER_SEC, CONTROL_PORT))


def execute_event(s, event):
    logging.getLogger(__name__).info('Update link:  %s' % ' '.join(event))
    try:
        if args.log:
            with open(args.log, 'a') as logfile:
                logfile.write('%f %s %d\n' % (time.time(), event[1], int(event[2])))
            logfile.closed

        logging.getLogger(__name__).info('Set bandwidth %dkb/s' % int(event[2]))
        s.sendall(('WRITE %s.rate %d\r\n' % (event[1], int(event[2]) * 128)).encode('utf-8'))
        logging.getLogger(__name__).info(s.recv(BUF_SIZE))
        
    except Exception as e:
        logging.getLogger(__name__).error(e)

def run_events():
    # Remove existing log file
    if args.log and os.path.isfile(args.log):
        os.remove(args.log)

    # Read event list
    events = []
    with open(args.events) as events_file:
        for line in strip_comments(events_file):
            events.append(line.split(' '))
    events_file.closed

    # Open control socket
    logging.getLogger(__name__).info("Establish control connection")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 7777))
    logging.getLogger(__name__).info(s.recv(BUF_SIZE))

    # Run events
    logging.getLogger(__name__).info('Running link events...')
    for event in events:
        # decide when to execute this event
        if event[0] is '*':
            raw_input('Press enter to run event:  %s' % ' '.join(event))
        else:
            try:
                time.sleep(float(event[0]))
            except:
                logging.getLogger(__name__).warning('Skipping invalid event: %s' % ' '.join(event))
                continue
        execute_event(s, event)
    s.close()

    logging.getLogger(__name__).info('Done running events.')

def start_servers():
    if servers_running():
        logging.getLogger(__name__).info('Some components already running...')
        stop_servers()

    logging.getLogger(__name__).info('Starting servers...')

    # Launch apache instances
    logging.getLogger(__name__).info('Configuring apache...')
    if args.topology == 'servers':
        with open(args.servers) as servers_file:
            for line in strip_comments(servers_file):
                servers.append('0.0.0.0:%d' % int(line))
                servers_port.append(int(line))
        servers_file.closed
        try:
            configure_apache(servers)
            restart_apache()
        except Exception as e:
            logging.getLogger(__name__).error(e)
    else:
        if args.topology == 'onelink':
            try:
                configure_apache(['0.0.0.0:8080'])
                restart_apache()
            except Exception as e:
                logging.getLogger(__name__).error(e)
        else:
            try:
                configure_apache(['0.0.0.0:8080', '0.0.0.0:8081'])
                restart_apache()
            except Exception as e:
                logging.getLogger(__name__).error(e)

        # Create click bandwidth shaper
        logging.getLogger(__name__).info('Creating bandwidth shaper...')
        autogen_click()
        run_bg('click %s.click' % args.topology)

    logging.getLogger(__name__).info('Network started.')

def stop_servers():
    logging.getLogger(__name__).info('Stopping simulated network...')

    # stop apache instances
    logging.getLogger(__name__).info('Stopping apache...')
    if args.topology == 'servers':
        servers = []
        with open(args.servers) as servers_file:
            for line in strip_comments(servers_file):
                servers.append(int(line))
        servers_file.closed
        try:
            reset_apache(servers)
            restart_apache()
        except Exception as e:
            logging.getLogger(__name__).error(e)
    else:
        if args.topology == 'onelink':
            try:
                reset_apache(['0.0.0.0:8080'])
                restart_apache()
            except Exception as e:
                logging.getLogger(__name__).error(e)
        else:
            try:
                reset_apache(['0.0.0.0:8080', '0.0.0.0:8081'])
                restart_apache()
            except Exception as e:
                logging.getLogger(__name__).error(e)

        # Destroy fake NICs
        logging.getLogger(__name__).info('Destroying bandwidth shaper...')
        try:
            check_both('killall -9 click', shouldPrint=False)
            time.sleep(0.1)
        except:
            pass
    logging.getLogger(__name__).info('Network stopped.')


def main():

    if args.command == 'start':
        if args.topology == 'servers' and args.servers == None:
            print("Please specify a servers port file using -s")
            return
        start_servers()
    elif args.command == 'run':
        if args.events == None:
            print("Please specify a event file using -e")
            return
        run_events()
    elif args.command == 'stop':
        if args.topology == 'servers' and args.servers == None:
            print("Please specify a servers port file using -s")
            return
        stop_servers()
    elif args.command == 'restart':
        if args.topology == 'servers' and args.servers == None:
            print("Please specify a servers port file using -s")
            return
        stop_servers()
        time.sleep(0.5)
        start_servers()

if __name__ == "__main__":
    # set up command line args
    parser = argparse.ArgumentParser(description='Launch bandwidth limited servers or multiple servers')
    parser.add_argument('topology', choices=['onelink', 'twolink', 'sharelink', 'servers'], help='topology of bandwidth limited servers')
    parser.add_argument('command', choices=['start','stop','restart','run'], help='start/stop/restart the servers, or run a series of link events?')
    parser.add_argument('-l', '--log', default=None, help='log file for logging events (overwrites file if it already exists)')
    parser.add_argument('-e', '--events', default=None, help='specify events file to use in place of the one contained in the topology directory')
    parser.add_argument('-s', '--servers', default=None, help='the file contains the port number of servers needed to be created in server mode')
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help='only print errors')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='print debug info. --quiet wins if both are present')
    args = parser.parse_args()
    
    # set up logging
    if args.quiet:
        level = logging.WARNING
    elif args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(
        format = "%(levelname) -10s %(asctime)s %(module)s:%(lineno) -7s %(message)s",
        level = level
    )

    main()

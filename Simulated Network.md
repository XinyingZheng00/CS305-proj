# Simulated Network

To test your system, you will run everything (proxies, servers, and DNS server) on a simulated network in the docker container.

### File Description  

***netsim/netsim.py*** 

This script controls the simulated network. It automatically starts an instance of Apache for you on each IP address listed in your topology’s `.servers` file. Each instance listens on port 8080 and is configured to serve files from /var/www; we have put sample video chunks here for you.

***netsim/apache_setup.py***

This file contains code used by netsim.py to start and stop Apache instances on the IP addresses in your .servers file; you do not need to interact with it directly.

***grapher.py*** 

A script to produce plots of link utilization, fairness, and smoothness from log files.

### Usage

```sh
python3 netsim.py -s servers/{#servers} servers start
python3 netsim.py {link} start
```






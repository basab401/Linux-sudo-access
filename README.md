# A Linux application to grant sudo access to the users

## Overview:
Here is a sample project to achieve the following goals:

  - A python application / script that adds users, being received over a REST interface (e.g., https://testdb.company.com/devices/`hostname`/allowedUsers) to the list of sudo users of an Ubuntu machine.
  - The script should run automatically whenever the system starts and it should run as a daemon.
  - Assume that the REST API returns a jsonified response something like below:
        { “allowedUsers”: [ “abc123”, “def456” ] }
  - Assume that once `hostname` in the URI changes, different values for allowedUsers are returned.


## Folder Structure:
```
tree
.
├── README.md
├── bin
│   └── sudo-access
├── build
│   ├── lib
│   │   └── sudo_access
│   │       ├── __init__.py
│   │       └── sudo_access.py
│   └── scripts-3.5
│       └── sudo-access
├── docker
│   └── Dockerfile
├── install_service
│   └── create_systemd_service.sh
├── requirements.txt
├── setup.cfg
├── setup.py
├── sudo_access
│   ├── __init__.py
│   └── sudo_access.py
├── supervisord
│   ├── sudo_access_service.conf
│   └── supervisord.conf
└── systemd
    └── sudo-access.service
```

## Applicaton details:

The python application accepts in the following optional command line arguments:
```
	--hostname:  REST API server hostname
	--port:      REST API server port
	--username:  REST Username
	--password:  REST Password
	--device_hostname:   Device hostname to calculate the REST resource
	--debug:     Dictates file and console log levels
```
Once started, the application periodically (currently every 60 seconds) invokes the REST API to fetch the allowed user list. Then if the received user exists on the system and not already part of sudo list, it tries to add the user into the sudo list and continue.

## Packaging and deployment:

### Install as a systemd service ==>
The python setup.py implements a custom 'install' class to enable the application as a systemd service on boot as well as start the service immediately.

Run the following command from the source root to install the python application and start/enable the same as a systemd service:
```
  sudo python3.6 setup.py install
```

### Install as a docker container ==>
This project also includes a Dockerfile that can install the application in the container and enable supervisord to start and monitor the service. User can utilise this container for mostly test purposes.

Run the following command from the source root to create a docker image:
```
  docker build  -f docker/Dockerfile  -t linux_sudo_access:latest .
```
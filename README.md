Kanompang
=========

Installing dependent packages
-----

    Installing lighttpd and php5
    $ sudo apt-get install lighttpd php5-cgi

    Configuring lighttpd for using php5-cgi
    $ sudo lighty-enable-mod fastcgi 
    $ sudo lighty-enable-mod fastcgi-php

    Installing Tornado Web Framework
    $ sudo apt-get install python-tornado


Preparing Code before running
-----

    1) Don't forget change the server's ipaddress in "web/device_list.html", "web/device_inner.html", "arduino-client/dht22/dht22.ino" and "arduino-client/ds18b20/ds18b20.ino" to your own server's ipaddress by searching for "<your_server_ip>" and change it.

    2) Don't forget change the Wi-Fi ssid and password in "web/device_inner.html" and "arduino-client/dht22/dht22.ino" to your own ssid and password by searching for "<your_ssid>", "<your_password>" and change it.


Running Server
-----
    
    Change current directory to "python-server"

    Run main python script
    $ python Kanompang.py

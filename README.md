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


Running Server
-----
	
	Change current directory to "python-server"

	Run main python script
	$ python Kanompang.py
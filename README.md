# couponfinder
Coupon Finder


To clone the couponfinder app, to my Django project.
1. Enter the django project (to the same level, as manage.py)
2. Run: git clone https://github.com/gregorymususa/couponfinder.git

THEN

Change the project's settings.py and urls.py

#settings.py#

ALLOWED_HOSTS

INSTALLED_APPS

DATABASES

#urls.py#
from django.urls import include
path('couponfinder/', include('couponfinder.urls')),


## For Fresh Servers
### Activate the virtual-env, THEN:
$ sudo apt-get install python-dev python3-dev

$ sudo apt-get install default-libmysqlclient-dev

$ pip install mysqlclient

## You will also need to install autopep8, for the virtual-env
$ pip install autopep8
gq    - to format line
gqap  - to format consecutive lines of code (i.e. no blank lines in-between)
gggqG - to format whole document

## You should conside installing autopep8, globally on the server
$ sudo apt-get install python-autopep8

## Project External Libraries - for crawler
$ pip install requests
$ pip install beautifulsoup4

## Install Web Server Apache, and Apache Module mod_wsgi
$ sudo apt-get install apache2
$ sudo apt-get install libapache2-mod-wsgi-py3

## Configure Apacahe
$ cd /etc/apache2/sites-available

$ sudo vim 000-default.conf
+--------------------------------
|<VirtualHost *:80>
|  <Directory /home/gunter/couponfinder-env/couponfinderproject/couponfinderproject>
|    <Files wsgi.py>
|      Require all granted
|    </Files>
|  </Directory>
|
|  WSGIDaemonProcess couponfinder python-home=/home/gunter/couponfinder-env python-path=/home/gunter/couponfinder-env/couponfinderproject
|  WSGIProcessGroup couponfinder
|  WSGIScriptAlias / /home/gunter/couponfinder-env/couponfinderproject/couponfinderproject/wsgi.py
|</VirtualHost>
+--------------------------------

$ sudo apache2ctl configtest
Syntax OK

$ sudo systemctl restart apache2



.

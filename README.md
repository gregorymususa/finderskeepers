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


## Fresh Droplet Environment Setup
### Install MYSQL Client
$ source bin/activate #activate virtual-env

$ sudo apt-get install python-dev python3-dev

$ sudo apt-get install default-libmysqlclient-dev

$ pip install mysqlclient

### Install PEP8
$ pip install autopep8

gq    - to format line

gqap  - to format consecutive lines of code (i.e. no blank lines in-between)

gggqG - to format whole document

### Install PEP8 globally
$ sudo apt-get install python-autopep8

### Install External Libraries
$ pip install requests

$ pip install beautifulsoup4

### Install Web Server Apache, and Apache Module mod_wsgi
$ sudo apt-get install apache2

$ sudo apt-get install libapache2-mod-wsgi-py3

### Configure Apacahe
$ cd /etc/apache2/sites-available

$ sudo vim 000-default.conf

```
<VirtualHost *:80>
  
  <Directory /home/gunter/couponfinder-env/couponfinderproject/couponfinderproject>

    <Files wsgi.py>
      
      Require all granted
    
    </Files>

  </Directory>

  WSGIDaemonProcess couponfinder python-home=/home/gunter/couponfinder-env python-path=/home/gunter/couponfinder-env/couponfinderproject
  
  WSGIProcessGroup couponfinder
  
  WSGIScriptAlias / /home/gunter/couponfinder-env/couponfinderproject/couponfinderproject/wsgi.py

</VirtualHost>
```

$ sudo apache2ctl configtest

Syntax OK

$ sudo systemctl restart apache2

### Setup Static Files
$ mkdir /var/www/couponfinder/static

$ vim /couponfinder-env/couponfinderproject/couponfinderproject/settings.py

```
STATIC_ROOT = '/var/www/static/'
```

$ sudo chmod 777 static/

$ ./manage.py collectstatic #this will create the 'couponfinder' directory, inside static

$ cd static

$ sudo chmod 777 -R couponfinder/ #change the mode of this folder, to give it write permissions

$ ./manage.py collectstatic


### Update Apache Config
$ sudo /etc/apache2/sites-available/vim 000-default.conf

```
Alias /static /var/www/static
<Directory /var/www/static/>
  Require all granted
</Directory>
```

$ sudo apache2ctl configtest

$ sudo systemctl restart apache2
.

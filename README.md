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
### Setup Virtual-Env and Django Project
$ virtualenv --python=python3 couponfinder-env

$ cd couponfinder-env

$ django-admin startproject couponfinderproject

### Install Django Apps
$ vim settings.py

INSTALLED_APPS = ['couponfinder.apps.CouponfinderConfig',.....]

### Install MYSQL Client (and configure it in settings.py)
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
#### Requests
$ pip install requests

#### Beautfiul Soup
$ pip install beautifulsoup4

#### SASS
$ sudo apt-get update

$ sudo apt-get install ruby-full rubygems

$ sudo gem install sass

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

## Company Logo processing
sudo apt-get update

sudo apt-get install imagemagick -y

wget --no-verbose --no-parent --recursive --level=1 --no-directories http://yetanothersandbox.com/logos/

#### Identify image dimensions
identify -format "%w x %h" image.png

#### Identify image format
identify -verbose output.png | grep Format

#### Convert image
sudo convert image.jpg image.png

#### Brutal resize
sudo convert image.png -resize 88x88\> image.jpg

#### Adding white space to rectangular images
sudo convert -size 504x504 xc:white canvas.png

sudo convert canvas.png target.png -geometry +0+200 -composite output.png

Create a canvas (of the desired size)

Make a composite of the canvas and the target image; use -geometry to offset the target image.

#### Adding a favicon.ico
```
$ cd ~..../couponfinder/static/couponfinder

$ sudo wget --no-verbose --no-parent --recursive --level=1 --no-directories http://yetanothersandbox.com/images/favicon-1.png
$ sudo wget --no-verbose --no-parent --recursive --level=1 --no-directories http://yetanothersandbox.com/images/favicon-2.png

$ convert favicon-1.png -define icon:auto-resize=64,48,32,16 favicon.ico
$ convert favicon-2.png -define icon:auto-resize=64,48,32,16 favicon.ico

$ ./manage.py collectstatic

$ vim base.html
<link rel="shortcut icon" href="{% static "couponfinder/favicon.ico" %}" type="image/x-icon">
```

### Thoughts on Algorithm
1. Create a command, that does the following:
2. Looks at all Organization.logo - IF an Organization has a blank (or what exists is not returing HTTP 200):
3. Go to static/couponfinder/logo/; and find an image containing the filename Organization.slug
4. IF the image is square, do nothing ELSE make the image square (imagemagic)
5. Add the new image name to Organization.logo
6. Flag rectangles, for manual intervention / make sure to only add square and close to square logos. 

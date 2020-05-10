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


## 1. Fresh Droplet Environment Setup
### 1.1. Setup Virtual-Env and Django Project
$ virtualenv --python=python3 couponfinder-env

$ cd couponfinder-env

$ django-admin startproject couponfinderproject

### 1.2. Install Django Apps
$ vim settings.py

INSTALLED_APPS = ['couponfinder.apps.CouponfinderConfig',.....]

### 1.3. Install MYSQL Client (and configure it in settings.py)
$ source bin/activate #activate virtual-env

$ sudo apt-get install python-dev python3-dev

$ sudo apt-get install default-libmysqlclient-dev

$ pip install mysqlclient

$ pip install pytz

### 1.4. Install PEP8
$ pip install autopep8

gq    - to format line

gqap  - to format consecutive lines of code (i.e. no blank lines in-between)

gggqG - to format whole document

### 1.5. Install PEP8 globally
$ sudo apt-get install python-autopep8

### 1.6. Install External Libraries
#### Requests
$ pip install requests

#### Beautfiul Soup
$ pip install beautifulsoup4

#### SASS
$ sudo apt-get update

$ sudo apt-get install ruby-full rubygems

$ sudo gem install sass

### 1.7. Install Web Server Apache, and Apache Module mod_wsgi
$ sudo apt-get install apache2

$ sudo apt-cache search wsgi #search for module name

$ sudo apt-get install libapache2-mod-wsgi-py3

### 1.8. Configure Apacahe
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

### 1.9. Setup Static Files
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

### 1.10. Project urls.py (nb. not the app urls.py)
from couponfinder import views

urlpatterns = [path('',views.index, name='home')]

### 1.11. Update Apache Config
$ sudo /etc/apache2/sites-available/vim 000-default.conf

```
Alias /static /var/www/static
<Directory /var/www/static/>
  Require all granted
</Directory>
```

$ sudo apache2ctl configtest

$ sudo systemctl restart apache2

### 1.12. Envrionment Variables

1. Tried to place Environment Variables in $ sudo vim /etc/environment (so it is available globally, from boot)

ENVIRONMENT_VARIABLE='VALUE'

(no need for export, before the variable)

2. Tried to place Environment Variables in $ sudo vim /etc/apache2/sites-available/000-default.conf (because System Environment Variables != Apache Environment Variables)

Using PassEnv, and SetEnv.

PassEnv: Specifies one or more native system environment variables to make available as internal environment variables, which are available to Apache HTTP Server modules as well as propagated to CGI scripts and SSI pages.

SetEnv: Sets an internal environment variable, which is then available to Apache HTTP Server modules, and passed on to CGI scripts and SSI pages.

Source: https://httpd.apache.org/docs/2.4/mod/mod_env.html#passenv

3. Succeeded when placing Environment Variables in $ vim /coupounfinderproject/couponfinderproject/wsgi.py (because wsgi.py was created for declaring Environment Variables for the Django Process)

os.environ['ENVIRONMENT_VARIABLE'] = 'VALUE'

Source: https://gist.github.com/GrahamDumpleton/b380652b768e81a7f60c

## 2. Company Logo processing
sudo apt-get update

sudo apt-get install imagemagick -y

wget --no-verbose --no-parent --recursive --level=1 --no-directories http://yetanothersandbox.com/logos/

#### 2.1. Custom Commands
../../../../manage.py resize_logos *

./manage.py collectstatic

sudo systemctl restart apache2

./manage.py load_logos slug slug slug 

#### 2.2. Adding a favicon.ico
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

### 2.3. Thoughts on Algorithm
1. Create a command, that does the following:
2. Looks at all Organization.logo - IF an Organization has a blank (or what exists is not returing HTTP 200):
3. Go to static/couponfinder/logo/; and find an image containing the filename Organization.slug
4. IF the image is square, do nothing ELSE make the image square (imagemagic)
5. Add the new image name to Organization.logo
6. Flag rectangles, for manual intervention / make sure to only add square and close to square logos. 

### 2.4. Versioning
We are using the versioning system: MAJOR.MINOR.PATCH

Given a new version, increment the:
- MAJOR version when you make incompatible API changes
- MINOR version when you add functionality in a backwards-compatible manner
- PATCH version when you make backwards-compatible bug fixes.

Source:
> https://blog.codeship.com/best-practices-when-versioning-a-release/

## 3. Force migrations 
### 3.1. Without MakeMigrations
manage.py migrate --syncdb
### 3.2. Fake first migrate
manage.py migrate --fake myappname zero

## 4. SSL Activation

### 4.1. Create Certificate Request
Request a CSR file
```
$ openssl req -new -newkey rsa:2048 -nodes -keyout discount-ted.com.key -out discount-ted.com.csr
```

```
Country Name (2 letter code) [AU]:NL
State or Province Name (full name) [Some-State]:Zuid Holland
Locality Name (eg, city) []:Rotterdam
Organization Name (eg, company) [Internet Widgits Pty Ltd]:Discount Ted
Organizational Unit Name (eg, section) []:Developers
Common Name (e.g. server FQDN or YOUR name) []:discount-ted.com
Email Address []:admin@discount-ted.com

Please enter the following 'extra' attributes
to be sent with your certificate request
A challenge password []:*******************
An optional company name []:
```

The following files will be created:
```
$ ls -l
discount-ted.com.csr
discount-ted.com.key
```

### 4.2. Check certificate
SSL Checker: https://decoder.link/

### 4.3. Request and Obtain Certificate
Enter CSR (including Header and Footer) on Namecheap's website (SSL Activation)
Namecheap will send data to Certificate Authority
Certificate Authority will email your
Follow the email instructions
Certificate Authority will send you the certificate; SFTP them onto the server
* discount-ted_com.ca-bundle
* discount-ted_com.crt

### 4.4. Install Certificate
Install Certificate; or
Replace the files that the directives point to

```
$ sudo vim /etc/apache2/sites-enabled/000-default.conf
```

```
# SSL Certificate Installation
ServerName discount-ted.com
SSLEngine on
SSLCertificateKeyFile .../discount-ted.com.key
SSLCertificateFile .../discount-ted_com.crt
SSLCACertificateFile .../discount-ted_com.ca-bundle
```

## 5. Encrypting Connection between Servers (MySQL)
* .csr - This is a Certificate Signing Request. Some applications can generate these for submission to certificate-authorities. The actual format is PKCS10 which is defined in RFC 2986. It includes some/all of the key details of the requested certificate such as subject, organization, state, whatnot, as well as the public key of the certificate to get signed. These get signed by the CA and a certificate is returned. The returned certificate is the public certificate (which includes the public key but not the private key), which itself can be in a couple of formats.
* .pem - Defined in RFCs 1421 through 1424, this is a container format that may include just the public certificate (such as with Apache installs, and CA certificate files /etc/ssl/certs), or may include an entire certificate chain including public key, private key, and root certificates. Confusingly, it may also encode a CSR (e.g. as used here) as the PKCS10 format can be translated into PEM. The name is from Privacy Enhanced Mail (PEM), a failed method for secure email but the container format it used lives on, and is a base64 translation of the x509 ASN.1 keys.
* .key - This is a PEM formatted file containing just the private-key of a specific certificate and is merely a conventional name and not a standardized one. In Apache installs, this frequently resides in /etc/ssl/private. The rights on these files are very important, and some programs will refuse to load these certificates if they are set wrong.
* .pkcs12 .pfx .p12 - Originally defined by RSA in the Public-Key Cryptography Standards (abbreviated PKCS), the "12" variant was originally enhanced by Microsoft, and later submitted as RFC 7292. This is a passworded container format that contains both public and private certificate pairs. Unlike .pem files, this container is fully encrypted. Openssl can turn this into a .pem file with both public and private keys: openssl pkcs12 -in file-to-convert.p12 -out converted-file.pem -nodes


A few other formats that show up from time to time:

* .der - A way to encode ASN.1 syntax in binary, a .pem file is just a Base64 encoded .der file. OpenSSL can convert these to .pem (openssl x509 -inform der -in to-convert.der -out converted.pem). Windows sees these as Certificate files. By default, Windows will export certificates as .DER formatted files with a different extension. Like...
* .cert .cer .crt - A .pem (or rarely .der) formatted file with a different extension, one that is recognized by Windows Explorer as a certificate, which .pem is not.
* .p7b .keystore - Defined in RFC 2315 as PKCS number 7, this is a format used by Windows for certificate interchange. Java understands these natively, and often uses .keystore as an extension instead. Unlike .pem style certificates, this format has a defined way to include certification-path certificates.
* .crl - A certificate revocation list. Certificate Authorities produce these as a way to de-authorize certificates before expiration. You can sometimes download them from CA websites.


In summary, there are four different ways to present certificates and their components:

* PEM - Governed by RFCs, its used preferentially by open-source software. It can have a variety of extensions (.pem, .key, .cer, .cert, more)
* PKCS7 - An open standard used by Java and supported by Windows. Does not contain private key material.
* PKCS12 - A Microsoft private standard that was later defined in an RFC that provides enhanced security versus the plain-text PEM format. This can contain private key material. Its used preferentially by Windows systems, and can be freely converted to PEM format through use of openssl.
* DER - The parent format of PEM. It's useful to think of it as a binary version of the base64-encoded PEM file. Not routinely used very much outside of Windows.


### 5.1. Generate a self signed root certificate

```
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out req.pem -days 365
```
Source: https://www.openssl.org/docs/man1.1.1/man1/req.html



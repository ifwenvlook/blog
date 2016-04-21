Blog
----
Preview: `http://www.vlblog.tech/`

A simple blog system based on Flask


Development
-----------

Prerequests:

1. python2.7/python3.4
2. mysql5.5+
3. Reference: Flask Web开发-基于Python的Web应用开发实战 `http://www.ituring.com.cn/book/1449`

Setup flask development:
	$ git clone `https://github.com/ifwenvlook/blog.git`

	$ cd /blog

	$ pip install -r requirements/dev.txt  



Quick Start
-----------
Create testdata and upgrade to mysql: 
	$ python manage.py db init

	$ python manage.py db migrate

	$ python manage.py datainit

	$ python manage.py db upgrade

	$ python manage.py runserver



Visit: `http://127.0.0.1:5000/`


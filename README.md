# Student Book Rental

## Features
* **Book** data fetched (initialized from `https://openlibrary.org/search.json?title={title}`)
* **Dashboard** with active rental listing with extend and return CTA for each list, quick actions (create new rental and initialize book) and student rental history
* **Book collection page** that listing all collection of Books in database, each list  has extended information (number of pages, monthly rental fee and availability) and CTA (rent book for if available and extend or return actions for rented book)
* **Student list page** will list all students with extended information for book rental and CTAs

![](https://medusadjango.s3.us-east-1.amazonaws.com/Screenshot+2024-11-21+at+11.54.40.png)

![](https://medusadjango.s3.us-east-1.amazonaws.com/Screenshot+2024-11-21+at+11.55.14.png)

![](https://medusadjango.s3.us-east-1.amazonaws.com/Screenshot+2024-11-21+at+11.55.31.png)

---

## Setup, Configure and Running
* Clone the repo `git clone git@github.com:niotech/studentbookrental.git`
* `cd studentbookrental`
* Configure `config/settings.py` as required, example: if you want to use different database engine or if you want to set DEBUG to False for production
* `pip install -r requirements.txt` to install all required python packages, I suggest to use python virtual environment
* `./manage.py migrate` to install the migrations to the databse
* `./manage.py createsuperuser` to create a superuser account so you can login into the system
* `./manage.py runserver` to run development server at default port :8000
* Open in your browser URL = `http://localhost:8000` login with the superuser account you just created (as superuser you may access django admin at `http://localhost:8000/admin/`)
* To initialized or adding Book data into the database, use quick actions **Initialize Books** use book title keywords such as "python django" to start adding book collection to the database
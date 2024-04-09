Package_name : Jetski
=====================

Jetski is a Python library for dealing with Jetski Rental System.

Installation
------------

Use the package manager `pip <https://pip.pypa.io/en/stable/>`__ to
install Jetski.

.. code:: bash

   pip install Jetski

Usage
-----

Start by importing both classes and datetime module.

.. code:: python

   from Jetski import JetskiRental, Customer
   import datetime

Then, create JetskiRental and Customer objects and test example of rent.

.. code:: python

   shop = JetskiRental(10)
   customer = Customer()

   jetskis = customer.requestJetski()

   customer.rentalBasis = 1

   customer.rentalTime = datetime.datetime.now() + datetime.timedelta(hours=-2)

   request = customer.returnJetski()

   shop.displaystock()

   shop.rentJetskiOnHourlyBasis(jetskis)

   shop.displaystock()

   bill = shop.returnJetski(request)

   print(f"Your bill is {bill}.")

Contributing
------------

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

Author
------

Tarid Suwansri

License
-------

`MIT <https://choosealicense.com/licenses/mit/>`__

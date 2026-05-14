Installation
============

Prerequisites
-------------

- Python 3.8 or newer
- `OpenCV <https://opencv.org/>`_ (installed via ``opencv-python``)
- A modern web browser

Steps
-----

1. **Clone the repository**

   .. code-block:: bash

      git clone https://github.com/your-org/game-annotator.git
      cd game-annotator

2. **Install Python dependencies**

   .. code-block:: bash

      pip install -r requirements.txt

   The key packages installed are:

   =============================  =============================================
   Package                        Purpose
   =============================  =============================================
   ``Django`` (5.1+)               Web framework
   ``opencv-python``              Video decoding and frame extraction
   ``Pillow``                     Image handling
   ``python-dotenv``              Environment variable loading from ``.env``
   =============================  =============================================

3. **Configure environment variables**

   .. code-block:: bash

      cp .env.example .env

   Open ``.env`` and set at minimum:

   .. code-block:: ini

      SECRET_KEY=<generate with the command below>
      DEBUG=True
      ALLOWED_HOSTS=localhost,127.0.0.1

   Generate a secret key:

   .. code-block:: bash

      python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

4. **Apply database migrations**

   .. code-block:: bash

      python manage.py migrate

5. **Start the development server**

   .. code-block:: bash

      python manage.py runserver

6. **Open the application**

   Navigate to http://localhost:8000 in your browser.

Optional: Admin Interface
--------------------------

Create a superuser to access the Django admin at ``/admin/``:

.. code-block:: bash

   python manage.py createsuperuser

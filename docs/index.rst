Contacts REST API
=================

Фінальне домашнє завдання до теми 13.

.. toctree::
   :maxdepth: 2
   :caption: Зміст

   api/modules

Опис
----

REST API для управління контактами з аутентифікацією, авторизацією за ролями,
кешуванням користувачів у Redis та механізмом скидання пароля.

Швидкий старт
-------------

.. code-block:: bash

   docker compose up --build

Запуск тестів
-------------

.. code-block:: bash

   pytest --cov=app --cov-report=term-missing

Генерація документації
----------------------

.. code-block:: bash

   cd docs
   sphinx-build -b html . _build/html


Python Package Documentation
==============================

.. toctree::
    :maxdepth: 2

    {% for package in packages %}
    {{ package.doc_name }}
    {%- endfor %}


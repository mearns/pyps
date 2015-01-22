
``{{ fullname }}`` package
==============================================================================

{% if children|length != 0 %}

.. toctree::
    :maxdepth: 1

    {% for module in children %}
    {{ module.doc_name }}
    {% endfor %}

{% endif %}

.. automodule:: {{ fullname }}
    :members:
    :undoc-members:
    :show-inheritance:


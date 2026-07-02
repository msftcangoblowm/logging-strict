YAML ABC
=========

Abstract Base Class.

Public API

.. code-block:: python

    from logging_strict import LoggingYamlType

Non-abstract methods:

- as_str

- setup       -- applicable only for the UI

- iter_yamls  -- search a (non-package) folder

- get_version -- staticmethod

- pattern     -- classmethod

.. py:data:: logging_strict.logging_yaml_abc.__all__
   :type: tuple[str, ...]
   :value: ("LoggingYamlType", "YAML_LOGGING_CONFIG_SUFFIX", "after_as_str_update_package_name", "setup_logging_yaml")

   Module object exports

.. automodule:: logging_strict.logging_yaml_abc
   :members:
   :undoc-members:
   :special-members:
   :private-members:
   :platform: Unix
   :synopsis: base class of logging_yaml implementations

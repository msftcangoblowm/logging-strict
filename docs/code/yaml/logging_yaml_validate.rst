YAML Validate
==============

.. py:module:: logging_strict.logging_yaml_validate
  :platform: Unix
  :synopsis: validate logging.config yaml using strictyaml schema

   Validate :py:mod:`logging.config` yaml files.

   Available as an:

   - :abbr:`ep (entrypoint)`

   - via pre-commit

   .. seealso::

      `Custom filters <https://docs.python.org/3/howto/logging-cookbook.html#using-filters-to-impart-contextual-information>`_
      use case

      logging.config
      `[spec] <https://docs.python.org/3/library/logging.config.html#dictionary-schema-details>`_

      :py:mod:`strictyaml.compound_types`

   **Limitations**

   1. :py:class:`logging.handlers.SMTPHandler` arg ``secure`` takes:

      - None

      - empty tuple

      - tuple[str]

      - tuple[str, str]

     Actual: tuple[] or tuple[typing.Any, ...]

     So can't prevent :code:`len(Sequence) > 2`

   2. :py:class:`logging.handlers.TimedRotatingFileHandler` arg ``asTime``

     :py:mod:`strictyaml <strictyaml.docs>` has no support for :py:class:`datetime.time`

   **Module private variables**

   .. py:data:: __all__
      :type: tuple[str, str]
      :value: ("schema_logging_config", "validate_yaml_dirty")

      Module exports

   **Module objects**

   .. py:function:: validate_yaml_dirty(yaml_snippet, schema = schema_logging_config)

      This designed with the intent to verify :py:mod:`logging.config` yaml

      In :py:mod:`logging.config` docs, all examples shown contain
      YAML flow_style.

      YAML flow style (incorrect)

      .. code-block:: text

         somelist: [item0, item1]

      Without flow style (Correct)

      .. code-block:: text

         somelist:
           - item0
           - item1


      Eventhough it's easy to fix the yaml,
      :py:func:`logging.config.dictConfig` will accept the non-fixed yaml

      Reluctantly ... allow flow style

      world+dog

      - refers to the :py:mod:`logging.config` docs

      - have based their code off the :py:mod:`logging.config` docs

      - won't be aware of yaml intricacies and intrigue

      :param yaml_snippet: :py:mod:`logging.config` YAML str
      :type yaml_snippet: str
      :param schema: :py:mod:`strictyaml <strictyaml.docs>` strict typing schema
      :type schema: strictyaml.validators.Validator | logging_strict.logging_yaml_validate.schema_logging_config
      :returns: YAML object. Pass this to each worker
      :rtype: strictyaml.representation.YAML | None

      .. seealso::

         `Modern way <https://github.com/python/cpython/pull/102885/files>`_
         of dealing with Traceback

   .. py:class:: schema_logging_config

      :py:mod:`strictyaml` schema for :py:mod:`logging.config` yaml files

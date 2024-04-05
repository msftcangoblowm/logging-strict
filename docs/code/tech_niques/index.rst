Techniques
=============

tech_niques which are logging related as well as code inspection

.. automodule:: logging_strict.tech_niques
   :members:
   :private-members:
   :undoc-members:
   :exclude-members: ClassAttribTypes
   :platform: Unix
   :synopsis: Export all technique helpers

   .. py:class:: ClassAttribTypes(enum.Enum)
      As understood by :py:obj:`inspect.classify_class_attrs`

      .. py:attribute:: CLASSMETHOD
         :type: str
         :value: 'class method'

         Is this a class classmethod?

      .. py:attribute:: STATICMETHOD
         :type: str
         :value: 'static method'

         Is this a class staticmethod

      .. py:attribute:: PROPERTY
         :type: str
         :value: 'property'

         Is this a class property?

      .. py:attribute:: METHOD
         :type: str
         :value: 'method'

         Is this a class normal method

      .. py:attribute:: DATA
         :type: str
         :value: 'data'

         Is this class data

.. tableofcontents::

.. _api_locals_unittest_tb:

==================
unittest tb_locals
==================

When creating unittest modules, **always** supply the param :code:`tb_locals=True`.

.. code-block:: text

   if __name__ == "__main__":  # pragma: no cover
       unittest.main(tb_locals=True)

Exactly like ^^

When running the unittest and an error occurs, the additional feedback from the
list of local variables and current values' can be indispensable.

Unfortunitely, the scope defaults to where the error was captured, **not**
where would like to debug, normally that scope defaults to the unittest function.
Which is not very useful and very frustrating to change.

.. _error_purposefully_cause:

The desperate way, to change the *list of local variables* scope, is
to purposefully introduce a non-syntax error in the code block of interest.

like :code:`print("hi mom!", stream=sys.stderr)`

^^ this is obviously wrong and that's the entire point. It's neither a
compile error nor a syntax error, it's just wrong usage which will be caught when
running the code never reaching the unittest assert statement.

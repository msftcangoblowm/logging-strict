.. this will be appended to README.rst

Changelog
=========

..

   Feature request
   .................

   - integrate with asz

   Known regressions
   ..................

   - strictyaml.scalar.Time does not exist. So field asTime can't be supported
   - strictyaml has no automated tests
   - strictyaml has no typing hint stubs. ignore_missing_imports

   Commit items for NEXT VERSION
   .................................

.. scriv-insert-here

.. _changes_0-1-1:

Version 0.1.1 — 2024-02-19
------------------------------------------------

In unittests, track down export of `*.worker.logging.config.yaml` to xdg user data dir, 
rather than to a temp folder. To test, monitor ~/.local/share/[prog name] unlink 
anything in that folder. Run, make coverage. The folder should remain empty

- test: prevent/redirect export of *.worker.logging.config.yaml to temp folder

.. _changes_0-1-0:

Version 0.1.0 — 2024-02-19
------------------------------------------------

- chore(setuptools-scm): semantic versioning. See constants.py, _version.py, and igor.py

- chore(isort): support extensions py and pyi

- chore(pre-commit): local repo bypasses hook. Once published local repo config unnecessary

- feat(pre-commit): hook validate-logging-strict-yaml

- feat: within a folder tree, use a pattern to extract package data files

- feat: validate logging.config yaml. Entrypoint logging_strict_validate_yaml

- feat(tech_niques): add context_locals

- feat(tech_niques): add logging_capture

- feat(tech_niques): add logging_redirect

- feat(tech_niques): add coverage_misbehaves. Detect if runner is coverage

- feat(tech_niques): add inspect a class interface

- feat: add two logging.config yaml files. One for app. One for worker

- test: add two dummy logging.config yaml files. One for app. One for worker

- feat(appdirs): package appdirs support. Chooses correct xdg folder

.. scriv-end-here

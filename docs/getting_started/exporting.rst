Exporting
==========

When
-----

Exports occur before the logging.config yaml files are needed. There
are two process types: worker and app

When an app is run, it exports the app logging configuration.

Right before a :py:class:`multiprocessing.pool.Pool` runs, it exports
the worker logging configuration.

Right before a thread or ThreadPool runs, G'd and Darwin sit down to decide
which calamity will befall you. Best to avoid that cuz Python logging module is
thread-safe. Changes to the logging.config in one thread affects them all
and those changes last as long as the app runs.

Safe means safe to remove you from the gene pool. Would be a great name for a
horror movie. Don't be in that movie.

Where / what
-------------

Export location (on linux): :code:`$HOME/.local/share/[package name]/`

This is xdg user data dir and the configuration is per package.
Python logging configurations' cascade!

Whats exported?

- one for the app

- At least one, for the multiprocessing workers

If a user|coder edits and makes a change, undo'ing those changes would be
considered quite rude, minimally, poor ettiquette.

So that gauntlets stay on and package authors live long fulfilling peaceful
uneventful lives, overwrite existing logging config yaml files never
happens. Although fully capable, just absolutely refuses to do so!

If confident no changes have been made, can manually delete (unlink).

There will be no need for gauntlets, can safely put those away.

Upgrade path
--------------

*How to upgrade a particular logging.config yaml file?*

Best to increment the version and switch the code base to use the latest version

Custom changes should be upstreamed.

*Preferred the previous version*

There currently isn't a means to change which logging.config yaml file
a package uses.

This sounds like a job for user preference database, gschema. Not yet
implemented

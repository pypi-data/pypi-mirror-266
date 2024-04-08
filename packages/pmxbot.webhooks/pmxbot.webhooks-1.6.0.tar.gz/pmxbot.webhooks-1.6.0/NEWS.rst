v1.6.0
======

Features
--------

- Instead of splitting lines, enqueue multiline messages, handled nicely by Slack. (#1)


v1.5.0
======

Features
--------

- Rely on PEP 420 for namespace package.
- Replace pkg_resources with importlib_resources, alleviating deprecation warning.


v1.4.0
======

Refreshed packaging.

Prefer more_itertools to jaraco.itertools.

v1.3.0
======

Refreshed packaging.

v1.2.1
======

Fix error in entry point for webhooks.

v1.2.0
======

To align with other plugins, instead supply ``manuscript.url``
for to resolve Manuscript URLs.

v1.1.0
======

Solicit Manuscript URL from config to provide clickable hyperlinks.

v1.0.0
======

Adopt webhooks implemnetation from jaraco.pmxbot.http 4.0.1.

``/fogbugz`` is now deprecated. Use ``/manuscript`` instead.

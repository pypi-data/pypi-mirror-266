Fietsboek
=========

<a href="https://gitlab.com/dunj3/fietsboek/-/pipelines">
    <img src="https://img.shields.io/gitlab/pipeline-status/dunj3/fietsboek?branch=master" alt="Pipeline status">
</a>
<a href="https://fietsboek.readthedocs.io">
    <img src="https://img.shields.io/readthedocs/fietsboek" alt="Documentation status">
</a>
<a href="https://pypi.org/project/fietsboek/">
    <img src="https://img.shields.io/pypi/v/fietsboek" alt="PyPI version">
</a>
<a href="https://www.gnu.org/licenses/agpl-3.0.en.html">
    <img src="https://img.shields.io/gitlab/license/dunj3/fietsboek" alt="License">
</a>
<a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/pypi/pyversions/fietsboek" alt="Python versions">
</a>

[Website](https://fietsboek.org) — [Documentation](https://docs.fietsboek.org)

Fietsboek is a self-hostable sharing site for GPX track recordings with social
features. The goal is to have an application like [MyTourbook][MyTourbook] that
runs as a web-service and allows sharing and discovering of new tracks.

Note that Fietsboek is early in development and a hobby project, as such many
features are still lacking.

[MyTourbook]: https://mytourbook.sourceforge.io/mytourbook/

Installation
------------

Setup instructions are in the
[documentation](https://docs.fietsboek.org/administration/installation.html)
([mirror](https://fietsboek.readthedocs.io/en/latest/administration/installation.html)).

Development
-----------

- Setup the environment:

      virtualenv .venv
      .venv/bin/pip install poetry
      .venv/bin/poetry install

- Adjust `development.ini` to your needs. Explanations of the configuration
  options are in the
  [documentation](https://docs.fietsboek.org/administration/configuration.html).
- Initialize the database:

      .venv/bin/alembic -c development.ini upgrade head

- Serve the code:

      .venv/bin/pserve development.ini --reload

- Hack away!

License
-------

    Fietsboek, the GPX web sharing project
    Copyright (C) 2022 Daniel Schadt

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.


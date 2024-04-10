go-inspector
================================

go-inspector is a utility to extract dependencies and symbols from Go binaries.
It is desigend to work as a ScanCode Toolkit plugin.

To install and use:

- Run ``pip install go-inspector``
- Use with ``scancode --json-pp - --go-symbol --verbose <PATH to a tree or file with Go binaries>``

The JSON output will contain various dependencies and symbols found in Go binaries if any.


- License: Apache-2.0 AND MIT AND BSD-3-Clause WITH LicenRef-scancode-google-patent-license-golang
- Copyright (c) nexB Inc., Mandiant, The Go Authors, Elliot Chance and others
- Homepage: https://github.com/nexB/go-inspector/

See the src/go_inspector/bin for detailed license and credits for bundled third-party packages.


Development
----------------

- Install requirements and dependencies using ``make dev``
- Then ``source venv/bin/activate``

Testing:

- To run tests: ``pytest -vvs``
- To regen test fixtures: ``SCANCODE_REGEN_TEST_FIXTURES=yes pytest -vvs``
- To update the bundled GoReSym, see src/bin/update.sh


How to re-generate test binaries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These are compiled (and committed) from code in tests/data/basic :

- Run ``go tool dist list`` to get all possible pairs of OSes and arches to compile the binary.
- Then build a OS/arch pair like this to get compiled binaries:
  ``GOOS=<OS> GOARCH=<arch> go build -o ./tests/data/basic/app_<OS>_exe ./tests/data/main.go``
- Make a copy and run strip of the Linux executable as "app_lin_exe_stripped"

  
Funding and sponsoring
---------------------------

This project is funded in part through:

- NGI0 Entrust https://nlnet.nl/entrust, a fund established by NLnet with
  financial support from the European Commission's Next Generation Internet https://ngi.eu program.
  Learn more at the NLnet project page https://nlnet.nl/purl2all. 

  |nlnet| and |ngi0entrust|

- Support from nexB Inc. |nexb|

- Generous support from users like you!


.. |nlnet| image:: https://nlnet.nl/logo/banner.png
    :target: https://nlnet.nl
    :width: 20%
    :alt: NLnet foundation logo

.. |ngi0entrust| image:: https://nlnet.nl/image/logos/NGI0_tag.svg
    :target: https://nlnet.nl/entrust
    :width: 20%
    :alt: NGI Zero Logo

.. |nexb| image:: https://nexb.com/wp-content/uploads/2022/04/nexB.svg
    :target: https://nexb.com
    :width: 20%
    :alt: nexB logo

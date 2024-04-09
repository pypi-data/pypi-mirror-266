##############
sequential tar
##############
|TestStatus| |PyPiStatus| |BlackStyle| |BlackPackStyle| |MITLicenseBadge|

A wrapper around ``tarfile`` which is deliberatly limited and simple.
The package ``sequential_tar`` is meant to ease the writing and reading
of tarfiles where the payload of the files within the tarfile is maent to
go through the program's memory. Here, only regular files can be written to a
tarfile and blocks different from regular files are ignored while reading.
This package is a good start when one plans to use tarfiles as containers for
programs to read data from directly into their memory without seeking or the
creation of temporary files.

modes
-----
When writing the next file to the tarfile, one can set the ``mode`` to
choose either text ``"t"`` or binary ``"b"``. Further a
compression can be applied by adding ``"|gz"`` to the ``mode``.
In the same manner, a ``mode`` can be set when reading a file from the tarfile.
This way, possible decompression and text/binary conversions can be taken care of
with just a few characters in the ``mode`` parameter.


::

    import sequential_tar as seqtar
    import os
    path = "test.tar"

Set the ``mode`` for each file while writing to the tarfile.

::

        with seqtar.open(path, "w") as tar:
            tar.write(
                name="1.txt",
                payload="I am text number 1.",
                mode="wt",
            )
            tar.write(
                name="2.txt.gz",
                payload="I am text number 2.",
                mode="wt|gz",
            )
            tar.write(
                name="3.bin.gz",
                payload=b"0123456789",
                mode="wb|gz",
            )
            tar.write(
                name="4.bin",
                payload=b"123-123-123-123-123-123-123",
                mode="wb",
            )


Set the ``mode`` for each file while reading from the tarfile.

::

        with seqtar.open(path, "r") as tar:
            item = next(tar)
            assert item.name == "1.txt"
            assert item.read(mode="rt") == "I am text number 1."

            item = next(tar)
            assert item.name == "2.txt.gz"
            assert item.read(mode="rt|gz") == "I am text number 2."

            item = next(tar)
            assert item.name == "3.bin.gz"
            assert item.read(mode="rb|gz") == b"0123456789"

            item = next(tar)
            assert item.name == "4.bin"
            assert item.read(mode="rb") == b"123-123-123-123-123-123-123"


.. |TestStatus| image:: https://github.com/cherenkov-plenoscope/sequential_tar/actions/workflows/test.yml/badge.svg?branch=main
    :target: https://github.com/cherenkov-plenoscope/sequential_tar/actions/workflows/test.yml

.. |PyPiStatus| image:: https://img.shields.io/pypi/v/sequential_tar
    :target: https://pypi.org/project/sequential_tar

.. |BlackStyle| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |BlackPackStyle| image:: https://img.shields.io/badge/pack%20style-black-000000.svg
    :target: https://github.com/cherenkov-plenoscope/black_pack

.. |MITLicenseBadge| image:: https://img.shields.io/badge/License-MIT-yellow.svg
    :target: https://opensource.org/licenses/MIT


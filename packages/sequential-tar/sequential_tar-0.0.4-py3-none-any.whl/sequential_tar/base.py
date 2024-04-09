import tarfile as buildin_tarfile
import io
import gzip


def open(name=None, mode="r", fileobj=None):
    """
    Read or write tar files in a sequential way without seeking.

    Parameters
    ----------
    path : str
        Path to file.
    mode : str
        Either of ['r', 'r|gz', 'w', 'w|gz']. The 't' for text can be added but
        is ignored.

    Returns
    -------
    reader/writer : Reader/Writer
        Depending on mode.
    """
    tarfile = buildin_tarfile.open(name=name, mode=mode, fileobj=fileobj)
    if "r" in tarfile.mode:
        return SequentialTarReader(tarfile=tarfile)
    elif "w" in tarfile.mode:
        return SequentialTarWriter(tarfile=tarfile)
    else:
        raise ValueError("mode must either contain 'r' or 'w'.")


def tarfile_add_regular_file(tarfile, name, payload, mode="wt"):
    if "b" in mode:
        payload_raw = payload
    elif "t" in mode:
        payload_raw = str.encode(payload)
    else:
        raise ValueError("mode must either contain 'b' or 't'.")

    if "|gz" in mode:
        payload_bytes = gzip.compress(payload_raw)
    else:
        payload_bytes = payload_raw

    TAR_BLOCK_SIZE = 512
    SIZE_WRITTEN = TAR_BLOCK_SIZE

    with io.BytesIO() as buff:
        tarinfo = buildin_tarfile.TarInfo(name)
        tarinfo.size = buff.write(payload_bytes)
        SIZE_WRITTEN += tarinfo.size
        buff.seek(0)
        tarfile.addfile(tarinfo, buff)
    return SIZE_WRITTEN


class SequentialTarItem:
    def __init__(self, tarinfo, raw):
        self.tarinfo = tarinfo
        self.name = self.tarinfo.name
        self.raw = raw

    def read(self, mode="rt"):
        assert "r" in mode
        assert not "w" in mode

        if "|gz" in mode:
            payload = gzip.decompress(self.raw)
        else:
            payload = self.raw

        if "b" in mode:
            out = payload
        elif "t" in mode:
            out = bytes.decode(payload)
        else:
            raise ValueError("mode must either contain 'b' or 't'.")

        return out

    def __repr__(self):
        return "{:s}(name='{:s}')".format(self.__class__.__name__, self.name)


class SequentialTarWriter:
    def __init__(self, tarfile):
        self.tarfile = tarfile

    def write(self, name, payload, mode="wt"):
        return tarfile_add_regular_file(
            tarfile=self.tarfile,
            name=name,
            payload=payload,
            mode=mode,
        )

    def close(self):
        self.tarfile.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __repr__(self):
        return "{:s}(tarfile='{:s}')".format(
            self.__class__.__name__, repr(self.tarfile)
        )


class SequentialTarReader:
    def __init__(self, tarfile):
        self.tarfile = tarfile

    def next(self):
        return self.__next__()

    def __next__(self):
        while True:
            tarinfo = self.tarfile.next()
            if tarinfo is None:
                raise StopIteration
            if tarinfo.isfile():
                break
        raw = self.tarfile.extractfile(tarinfo).read()
        return SequentialTarItem(tarinfo=tarinfo, raw=raw)

    def __iter__(self):
        return self

    def close(self):
        self.tarfile.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __repr__(self):
        return "{:s}(tarfile='{:s}')".format(
            self.__class__.__name__, repr(self.tarfile)
        )

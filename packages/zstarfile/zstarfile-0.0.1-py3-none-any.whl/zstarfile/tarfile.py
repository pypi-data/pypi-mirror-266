# Copyright (C) 2024 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import shutil
import tarfile as _tarfile
from typing import IO, TYPE_CHECKING, Callable, Literal, TypeVar, cast

if TYPE_CHECKING:
    from _typeshed import StrOrBytesPath, StrPath

_TarFileT = TypeVar("_TarFileT", bound=_tarfile.TarFile)


class _TarFile(_tarfile.TarFile):
    """
    `tarfile.TarFile` subclass that uses the data_filter (introduced in PEP 706)
    when available
    """

    if hasattr(_tarfile, "data_filter"):
        extraction_filter = staticmethod(_tarfile.data_filter)


class ZSPlainTarfile(_tarfile.TarFile):
    """
    Same as `ZSTarfile` without the data_filter default
    """

    OPEN_METH = {  # noqa: RUF012
        **_tarfile.TarFile.OPEN_METH,
        "zst": "zstopen",
        "lz4": "lz4open",
    }

    @classmethod
    def zstopen(
        cls: type[_TarFileT],
        name: StrOrBytesPath | None = None,
        mode: Literal["r", "w", "x"] = "r",
        fileobj: IO[bytes] | None = None,
        compresslevel=3,
        **kwargs,
    ) -> _TarFileT:
        if mode not in {"r", "w", "x"}:
            raise ValueError("mode must be 'r', 'w' or 'x'")

        try:
            import zstandard
        except ImportError:  # pragma: no cover
            raise _tarfile.CompressionError(
                "zstandard module is not available"
            ) from None

        fileobj = (
            fileobj
            if fileobj
            else open(cast("str|bytes", name), mode + "b")  # noqa: SIM115
        )
        if mode == "r":
            decomp = zstandard.ZstdDecompressor()
            fileobj = decomp.stream_reader(fileobj, closefd=True)
        else:
            comp = zstandard.ZstdCompressor(level=compresslevel)
            fileobj = comp.stream_writer(fileobj)
        try:
            # Try to read a single byte to check for errors
            if mode == "r":
                fileobj.read(1)
            tarobj = cls.taropen(name, mode, fileobj, **kwargs)
        except zstandard.ZstdError as exc:
            fileobj.close()
            if mode == "r":
                raise _tarfile.ReadError("not a zstd file") from exc
            raise
        except:  # pragma: no cover
            fileobj.close()
            raise
        tarobj._extfileobj = False  # type: ignore[attr-defined]
        return tarobj

    @classmethod
    def lz4open(
        cls: type[_TarFileT],
        name: StrOrBytesPath | None = None,
        mode: Literal["r", "w", "x"] = "r",
        fileobj: IO[bytes] | None = None,
        compresslevel: int = 0,
        **kwargs,
    ) -> _TarFileT:
        if mode not in {"r", "w", "x"}:
            raise ValueError("mode must be 'r', 'w' or 'x'")

        try:
            import lz4.frame
        except ImportError:  # pragma: no cover
            raise _tarfile.CompressionError("lz4 module is not available") from None

        fileobj = cast(
            "IO[bytes]",
            lz4.frame.LZ4FrameFile(name, mode=mode, compression_level=compresslevel),
        )

        try:
            tarobj = cls.taropen(name, mode, fileobj, **kwargs)
        except RuntimeError as exc:
            fileobj.close()
            if mode == "r":
                raise _tarfile.ReadError("not a lz4 file") from exc
            raise
        except:  # pragma: no cover
            fileobj.close()
            raise
        tarobj._extfileobj = False  # type: ignore[attr-defined]
        return tarobj


class ZSTarfile(ZSPlainTarfile, _TarFile):
    """
    `TarFile` subclass that supports Zstandard and lz4 compression
    and uses the data_filter (introduced in PEP 706) by default.
    """


# Code is considered trivial enough to copy w/o copyright concerns
def _unpack_tarfile(
    filename: StrPath,
    extract_dir: StrPath,
    *,
    filter: Callable | None = None,  # noqa: A002
) -> None:
    """
    Derivation of `_unpack_tarfile()` that uses our TarFile subclass.
    """
    try:
        tarobj = ZSPlainTarfile.open(filename)
    except _tarfile.TarError as exc:
        raise shutil.ReadError(
            f"{filename} is not a compressed or uncompressed tar file"
        ) from exc
    try:
        tarobj.extractall(extract_dir, filter=filter)
    finally:
        tarobj.close()


shutil.register_unpack_format(
    "zsttar", [".tar.zst", ".tzst"], _unpack_tarfile, [], "zst'ed tar-file"
)
shutil.register_unpack_format(
    "lz4tar", [".tar.lz4", ".tlz4"], _unpack_tarfile, [], "lz4'ed tar-file"
)

# TODO: Support shutil.make_archive()

__all__ = ("ZSTarfile", "ZSPlainTarfile")

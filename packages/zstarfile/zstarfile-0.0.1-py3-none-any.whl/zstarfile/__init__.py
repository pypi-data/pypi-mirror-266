# Copyright (C) 2024 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: MIT

"""
tarfile extension with additional compression algorithms and PEP 706 by default
"""

from __future__ import annotations

from .tarfile import ZSPlainTarfile, ZSTarfile

__version__ = "0.0.1"

__all__ = ("ZSTarfile", "ZSPlainTarfile", "__version__")

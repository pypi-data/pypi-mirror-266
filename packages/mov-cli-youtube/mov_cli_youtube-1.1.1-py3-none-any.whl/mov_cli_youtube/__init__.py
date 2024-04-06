from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mov_cli.plugins import PluginHookData

from .youtube import *

plugin: PluginHookData = {
    "version": 1, 
    "scrapers": {
        "DEFAULT": YouTubeScraper, 
    }
}

__version__ = "1.1.1"
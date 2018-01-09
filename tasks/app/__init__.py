# encoding: utf-8
"""
Application related tasks for Invoke.
"""

from invoke import Collection

from catalog.config import BaseConfig
from . import run

namespace = Collection(
    run,
)

namespace.configure({
    'app': {
        'static_root': BaseConfig.STATIC_ROOT,
    }
})

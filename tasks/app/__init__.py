# encoding: utf-8
"""
Application related tasks for Invoke.
"""

from invoke import Collection

from catalog.config import BaseConfig
from . import deps, env, db, run, users, swagger

namespace = Collection(
    deps,
    env,
    db,
    run,
    users,
    swagger,
)

namespace.configure({
    'app': {
        'static_root': BaseConfig.STATIC_ROOT,
    }
})

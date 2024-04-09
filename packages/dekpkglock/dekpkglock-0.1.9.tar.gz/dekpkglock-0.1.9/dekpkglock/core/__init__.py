from .base import all_package_locker
from .pdm import *


def lock_path(name, path, remove=True):
    return all_package_locker[name]().lock(path, remove)


def patch_lock(name, path, index=0):
    all_package_locker[name]().patch(path, index)

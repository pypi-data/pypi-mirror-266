import os
import toml
from dektools.file import read_text, write_file, remove_path
from dektools.shell import shell_wrapper
from .base import PackageLockerBase, register_package_locker


@register_package_locker()
class PdmPackageLocker(PackageLockerBase):
    name = 'pdm'
    package_file = 'pyproject.toml'
    lock_file = 'pdm.lock'

    def get_package_meta(self, filepath):
        data = toml.loads(read_text(filepath))
        entry = data.get(self.module_name)
        if entry:
            return {'version': data.get('version'), **entry}

    def patch_lock(self, file_package, file_lock):
        local_file_lock = os.path.join(os.path.dirname(file_package), self.lock_file)
        if os.path.isfile(local_file_lock):
            write_file(file_lock, c=local_file_lock)
        else:
            path = os.path.dirname(write_file(None, t=True, c=file_package))
            shell_wrapper('pdm install', chdir=path)
            write_file(file_lock, c=os.path.join(path, self.lock_file))
            remove_path(path)

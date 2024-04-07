import os
from pathlib import Path
from dektools.file import list_dir, write_file, remove_path


class PackageLockerBase:
    name = None
    module_name = __name__.partition(".")[0]
    package_file = None
    lock_file = None
    path_resources = [Path(__file__).resolve().parent.parent.parent / 'resources']

    def lock(self, path, remove=True):
        result = self.resolve_package_lock(path)
        for k, v in result.items():
            if remove:
                remove_path(self.get_package_lockfile(k))
            if os.path.isfile(v):
                self.lock_package(k, v)
        return bool(result)

    def patch(self, path, index=0):
        unique = set()
        for fp, lock_file in self.find_package_lock(path):
            if lock_file not in unique and lock_file.startswith(str(self.path_resources[index])):
                self.patch_lock(fp, lock_file)
                unique.add(lock_file)

    def find_package_lock(self, path):
        for fp in list_dir(path):
            if self.is_hit(fp):
                meta = self.get_package_meta(fp)
                if meta:
                    path_package_rp = meta['path']
                    for path_res in self.path_resources:
                        yield fp, os.path.join(
                            path_res, self.name, path_package_rp, meta['version'], self.lock_file
                        )

    def resolve_package_lock(self, path):
        result = {}
        for fp, lock_file in self.find_package_lock(path):
            result[fp] = lock_file
        return result

    def lock_package(self, file_package, file_lock):
        write_file(self.get_package_lockfile(file_package), c=file_lock)

    def is_hit(self, filepath):
        return os.path.basename(filepath) == self.package_file

    def get_package_lockfile(self, filepath):
        return os.path.join(os.path.dirname(filepath), self.lock_file)

    def get_package_meta(self, filepath):
        raise NotImplementedError

    def patch_lock(self, file_package, file_lock):
        raise NotImplementedError


all_package_locker = {}


def register_package_locker(name=None):
    def wrapper(cls):
        all_package_locker[name or cls.name] = cls
        return cls

    return wrapper

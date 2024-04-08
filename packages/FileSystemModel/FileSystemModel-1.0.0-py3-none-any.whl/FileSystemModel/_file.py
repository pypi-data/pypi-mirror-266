# coding: utf-8

import os
import pywintypes
import win32security


class File:

    def __init__(self, path: str):
        try:
            file_security = win32security.GetFileSecurity(path, win32security.OWNER_SECURITY_INFORMATION)
            security_descriptor_owner = file_security.GetSecurityDescriptorOwner()
            account, domain, _ = win32security.LookupAccountSid(None, security_descriptor_owner)
            self.owner: str = domain + '\\' + account
        except pywintypes.error:
            self.owner: str = '...'
        self.name: str = os.path.basename(path)
        self.size: int = os.path.getsize(path)
        self.ctime: int = int(os.path.getctime(path))
        self.mtime: int = int(os.path.getmtime(path))
        self.readable: bool = os.access(path, os.R_OK)
        self.writable: bool = os.access(path, os.W_OK)
        self.executable: bool = os.access(path, os.X_OK)

    def __str__(self):
        return (f'File('
                f'name={self.name!r}, '
                f'size={self.size!r}, '
                f'ctime={self.ctime!r}, '
                f'mtime={self.mtime!r}, '
                f'owner={self.owner!r}), '
                f'readable={self.readable!r}, '
                f'writable={self.writable!r}, '
                f'executable={self.executable!r})')

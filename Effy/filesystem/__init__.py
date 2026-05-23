from __future__ import annotations
import os
import sys
from Effy.types import Effect
from Effy.filesystem.rwops import RWops, rw_from_file, rw_to_file

def get_base_path() -> Effect[str]:
    """Return the directory where the application executable is located."""
    def _run() -> str:
        """Thunk implementing base path resolution logic."""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(sys.argv[0]))
    return Effect(_run)

def get_pref_path(org: str, app: str) -> Effect[str]:
    """Return the directory where the application can write files."""
    def _run() -> str:
        """Thunk implementing preferences path resolution and creation logic."""
        if os.name == 'nt':
            base = os.environ.get('APPDATA', os.path.expanduser('~'))
        elif os.name == 'posix':
            base = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
        else:
            base = os.path.expanduser('~')
            
        path = os.path.join(base, org, app)
        os.makedirs(path, exist_ok=True)
        return path
    return Effect(_run)
__all__ = ["get_base_path", "get_pref_path", "RWops", "rw_from_file", "rw_to_file"]

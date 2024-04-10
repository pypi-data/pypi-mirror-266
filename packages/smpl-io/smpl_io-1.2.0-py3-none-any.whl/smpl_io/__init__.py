"""A collection of simplified utilities."""

from importlib.metadata import version

package = "smpl_io"

try:
    __version__ = version(package)
except:
    __version__ = "unknown"

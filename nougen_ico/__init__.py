"""
NouGenIco — Autonomous, zero-bloat Windows folder icon pipeline and media skinner.
"""

__version__ = "1.0.0"
__author__ = "Dav3 Meralus / Who Visions"

from .skinner import apply_portable_skin, is_folder_skinned
from .normalizer import clean_series_name, sanitize_filename

__all__ = [
    "apply_portable_skin",
    "is_folder_skinned",
    "clean_series_name",
    "sanitize_filename",
]

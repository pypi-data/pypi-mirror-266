"""
LoginMethod model
"""

from dataclasses import dataclass, field
from typing import Optional

from . import VersionedModel


@dataclass
class LoginMethod(VersionedModel):
    """A login method model."""

    person: str = field(default=None, metadata={
        'relationship': {'model': 'Person'},
        'field_type': 'entity_id'
    })
    method_type: Optional[str] = None
    method_data: Optional[dict] = None
    email: Optional[str] = field(default=None, metadata={
        'relationship': {'model': 'Email'},
        'field_type': 'entity_id'
    })
    password: Optional[str] = None

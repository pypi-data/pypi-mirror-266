"""
OtpMethod model
"""

from dataclasses import dataclass, field

from . import VersionedModel


@dataclass
class OtpMethod(VersionedModel):
    """An OTP method model."""

    person: str = field(default=None, metadata={
        'relationship': {'model': 'Person'},
        'field_type': 'entity_id'
    })
    secret: str = None
    name: str = None
    enabled: bool = False

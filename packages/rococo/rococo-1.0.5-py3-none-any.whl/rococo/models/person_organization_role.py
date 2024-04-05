"""
PersonOrganizationRole model
"""

from dataclasses import dataclass, field

from . import VersionedModel

# from enum import Enum

# class PersonOrganizationRoleEnum(Enum):
#     OWNER = "OWNER"
#     MANAGER = "MANAGER"
#     MEMBER = "MEMBER"

@dataclass
class PersonOrganizationRole(VersionedModel):
    """A person organization role model."""

    person: str = field(default=None, metadata={
        'relationship': {'model': 'Person'},
        'field_type': 'entity_id'
    })
    organization: str = field(default=None, metadata={
        'relationship': {'model': 'Organization'},
        'field_type': 'entity_id'
    })
    
    # TODO: We would benefit from strictly typed Enum for role, but flexibility would lower
    # role: PersonOrganizationRoleEnum = PersonOrganizationRoleEnum.MEMBER
    role: str = None

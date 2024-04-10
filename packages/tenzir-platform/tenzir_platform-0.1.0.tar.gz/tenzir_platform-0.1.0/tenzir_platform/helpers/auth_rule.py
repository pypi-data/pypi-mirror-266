from pydantic import BaseModel
from typing import Literal


class RoleAndOrganizationRule(BaseModel):
    """
    Grants access to users who have some role in some organization.
    """

    auth_fn: Literal["auth_organization_role"] = "auth_organization_role"
    connection: str

    # The required role.
    roles_claim: str
    role: str

    # The required organization.
    organization_claim: str
    organization: str


class OrganizationMembershipRule(BaseModel):
    """
    Grants access to users that belong to some organization.
    """

    auth_fn: Literal["auth_organization"] = "auth_organization"
    connection: str
    organization_claim: str
    organization: str


class EmailDomainRule(BaseModel):
    """
    Grants access for users from a specific connection (e.g. gmail)
    having email addresses from a given domain (e.g. @tenzir.com)
    """

    auth_fn: Literal["auth_email_suffix"] = "auth_email_suffix"
    connection: str
    email_domain: str


class UserAuthRule(BaseModel):
    auth_fn: Literal["auth_user"] = "auth_user"
    user_id: str


AuthRule = (
    UserAuthRule
    | EmailDomainRule
    | RoleAndOrganizationRule
    | OrganizationMembershipRule
)

from gql import gql
from typing import Sequence

class updateMethods:

    _UpdateOrganizationQuery = """
    mutation UpdateOrganization($org_id: Int!, $changes: Organizations_set_input!) {
  update_Organizations(where: {id: {_eq: $org_id}}, _set: $changes) {
    returning {
      billing_contact
      company_name
      domain
      email_domain
      id
      max_total_request_count
      owner
      plan_id
      stripe_customer_id
      stripe_subscription_id
      technical_contact
    }
  }
}
    """

    def UpdateOrganization(self, org_id: int, changes: dict):
        query = gql(self._UpdateOrganizationQuery)
        variables = {
            "org_id": org_id,
            "changes": changes,
        }
        operation_name = "UpdateOrganization"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _UpdateOrganizationAllowedDomainsQuery = """
    mutation UpdateOrganizationAllowedDomains($org_id: Int!, $allowed_domains: _varchar!) {
  update_Organizations_by_pk(pk_columns: {id: $org_id}, _set: {allowed_domains: $allowed_domains}) {
    allowed_domains
  }
}
    """

    def UpdateOrganizationAllowedDomains(self, org_id: int, allowed_domains: dict):
        query = gql(self._UpdateOrganizationAllowedDomainsQuery)
        variables = {
            "org_id": org_id,
            "allowed_domains": allowed_domains,
        }
        operation_name = "UpdateOrganizationAllowedDomains"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

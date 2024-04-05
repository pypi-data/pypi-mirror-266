from gql import gql
from typing import Sequence

class getMethods:

    _GetOrganizationAllowedDomainsQuery = """
    query GetOrganizationAllowedDomains($org_id: Int!) {
  Organizations(where: {id: {_eq: $org_id}}) {
    allowed_domains
  }
}
    """

    def GetOrganizationAllowedDomains(self, org_id: int):
        query = gql(self._GetOrganizationAllowedDomainsQuery)
        variables = {
            "org_id": org_id,
        }
        operation_name = "GetOrganizationAllowedDomains"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

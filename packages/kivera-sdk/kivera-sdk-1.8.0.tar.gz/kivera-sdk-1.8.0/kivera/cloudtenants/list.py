from gql import gql
from typing import Sequence

class listMethods:

    _ListCloudTenantsQuery = """
    query ListCloudTenants {
    CloudTenants {
        id
        name
        organization_id
        Provider {
            id
            name
        }
    }
}
    """

    def ListCloudTenants(self):
        query = gql(self._ListCloudTenantsQuery)
        variables = {
        }
        operation_name = "ListCloudTenants"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

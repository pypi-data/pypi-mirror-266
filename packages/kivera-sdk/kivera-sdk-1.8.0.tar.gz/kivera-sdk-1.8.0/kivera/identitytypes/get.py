from gql import gql
from typing import Sequence

class getMethods:

    _GetIdentityTypeQuery = """
    query GetIdentityType($id: Int!){
  IdentityTypes_by_pk(id: $id) {
    config
    id
    identity_type
  }
}
    """

    def GetIdentityType(self, id: int):
        query = gql(self._GetIdentityTypeQuery)
        variables = {
            "id": id,
        }
        operation_name = "GetIdentityType"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

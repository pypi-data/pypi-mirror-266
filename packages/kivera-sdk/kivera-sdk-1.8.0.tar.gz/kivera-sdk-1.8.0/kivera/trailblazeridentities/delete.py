from gql import gql
from typing import Sequence

class deleteMethods:

    _DeleteTrailBlazerIdentityQuery = """
    mutation DeleteTrailBlazerIdentity($id: Int!) {
  update_TrailBlazerIdentities( where: {id: {_eq: $id}}, _set: {deleted: false}) {
    returning {
      deleted
      id
      identity_id
      trailblazer_id
    }
  }
}
    """

    def DeleteTrailBlazerIdentity(self, id: int):
        query = gql(self._DeleteTrailBlazerIdentityQuery)
        variables = {
            "id": id,
        }
        operation_name = "DeleteTrailBlazerIdentity"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

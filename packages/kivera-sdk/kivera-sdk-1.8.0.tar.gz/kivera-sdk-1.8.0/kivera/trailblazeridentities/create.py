from gql import gql
from typing import Sequence

class createMethods:

    _CreateTrailBlazerIdentityQuery = """
    mutation CreateTrailBlazerIdentity($trailblazer_id: Int!, $identity_id: Int!) {
  insert_TrailBlazerIdentities(objects: {identity_id: $identity_id, trailblazer_id: $trailblazer_id, deleted: false}) {
    returning {
      deleted
      id
      identity_id
      trailblazer_id
    }
  }
}
    """

    def CreateTrailBlazerIdentity(self, trailblazer_id: int, identity_id: int):
        query = gql(self._CreateTrailBlazerIdentityQuery)
        variables = {
            "trailblazer_id": trailblazer_id,
            "identity_id": identity_id,
        }
        operation_name = "CreateTrailBlazerIdentity"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

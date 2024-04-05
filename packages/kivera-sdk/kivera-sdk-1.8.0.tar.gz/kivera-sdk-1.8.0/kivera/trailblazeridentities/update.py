from gql import gql
from typing import Sequence

class updateMethods:

    _UpdateTrailBlazerIdentityQuery = """
    mutation UpdateTrailBlazerIdentity($trailblazer_id: Int!, $identity_id: Int!, $id: Int!, $deleted: Boolean!) {
  update_TrailBlazerIdentities( where: {id: {_eq: $id}}, _set: {identity_id: $identity_id, deleted: $deleted, trailblazer_id: $trailblazer_id}) {
    returning {
      deleted
      id
      identity_id
      trailblazer_id
    }
  }
}
    """

    def UpdateTrailBlazerIdentity(self, trailblazer_id: int, identity_id: int, id: int, deleted: bool):
        query = gql(self._UpdateTrailBlazerIdentityQuery)
        variables = {
            "trailblazer_id": trailblazer_id,
            "identity_id": identity_id,
            "id": id,
            "deleted": deleted,
        }
        operation_name = "UpdateTrailBlazerIdentity"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

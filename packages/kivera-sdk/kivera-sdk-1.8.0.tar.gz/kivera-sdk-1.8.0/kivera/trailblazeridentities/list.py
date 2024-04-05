from gql import gql
from typing import Sequence

class listMethods:

    _ListTrailBlazerIdentitiesQuery = """
    query ListTrailBlazerIdentities {
  TrailBlazerIdentities(where: {deleted: {_eq: false}, Identity: {IdentityType: {identity_type: {_eq: "CLOUDTENANT"}}}}) {
    deleted
    id
    identity_id
    trailblazer_id
    Identity {
      name
      description
      type_id
    }
  }
}
    """

    def ListTrailBlazerIdentities(self):
        query = gql(self._ListTrailBlazerIdentitiesQuery)
        variables = {
        }
        operation_name = "ListTrailBlazerIdentities"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

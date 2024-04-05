from gql import gql
from typing import Sequence

class updateMethods:

    _UpdateTrailBlazerQuery = """
    mutation UpdateTrailBlazer($description: String!, $id: Int!, $identities: [TrailBlazerIdentities_insert_input!]!, $tags: jsonb!, $debug: Boolean!) {
  update_TrailBlazers(where: {id: {_eq: $id}}, _set: {description: $description, tags: $tags}) {
    returning {
      id
      deleted
      description
      name
      org_id
      status
    }
  }
  update_TrailBlazerSettings(where: {trailblazer_id: {_eq: $id}}, _set: {debug: $debug}) {
    affected_rows
  }
  insert_TrailBlazerIdentities(objects: $identities, on_conflict: {constraint: TrailBlazerIdentities_uniq_key, update_columns: [identity_id, deleted]}) {
    returning {
      id
      deleted
      identity_id
      trailblazer_id
    }
  }
  update_TrailBlazerIdentities(where: {trailblazer_id: {_eq: $id}}, _set: {}) {
    affected_rows
  }
}
    """

    def UpdateTrailBlazer(self, description: str, id: int, identities: Sequence[dict], tags: dict, debug: bool):
        query = gql(self._UpdateTrailBlazerQuery)
        variables = {
            "description": description,
            "id": id,
            "identities": identities,
            "tags": tags,
            "debug": debug,
        }
        operation_name = "UpdateTrailBlazer"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _UpdateTrailblazerStatusQuery = """
    mutation UpdateTrailblazerStatus($trailblazer_id: Int!, $status: String) {
    update_TrailBlazers(where: {id: {_eq: $trailblazer_id }}, _set: { status: $status }) {
        returning {
            id
            status
        }
    }
}
    """

    def UpdateTrailblazerStatus(self, trailblazer_id: int, status: str = None):
        query = gql(self._UpdateTrailblazerStatusQuery)
        variables = {
            "trailblazer_id": trailblazer_id,
            "status": status,
        }
        operation_name = "UpdateTrailblazerStatus"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

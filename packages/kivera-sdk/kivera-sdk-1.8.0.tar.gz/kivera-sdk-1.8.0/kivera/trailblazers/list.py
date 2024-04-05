from gql import gql
from typing import Sequence

class listMethods:

    _ListTrailBlazersQuery = """
    query ListTrailBlazers($orgID: Int!) {
  TrailBlazers(where: {deleted: {_eq: false}, org_id: {_eq: $orgID}}) {
    description
    healthcheck_info
    id
    name
    org_id
    status
    tags
    TrailBlazerSettings {
      debug
      id
      trailblazer_mode
    }
    TrailBlazerIdentities(where: {deleted: {_eq: false}}) {
      identity_id
      trailblazer_id
      deleted
    }
    TrailBlazerCounters_aggregate{
      aggregate {
        sum {
          counter_accepts
          counter_denials
          counter_notifies
          counter_total_request
        }
      }
    }
  }
}
    """

    def ListTrailBlazers(self, orgID: int):
        query = gql(self._ListTrailBlazersQuery)
        variables = {
            "orgID": orgID,
        }
        operation_name = "ListTrailBlazers"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

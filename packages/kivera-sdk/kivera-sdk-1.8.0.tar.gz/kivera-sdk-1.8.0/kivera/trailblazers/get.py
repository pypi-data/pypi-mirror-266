from gql import gql
from typing import Sequence

class getMethods:

    _GetTrailBlazerAndIdentitiesQuery = """
    query GetTrailBlazerAndIdentities($trailblazer_id: Int!) {
  TrailBlazers_by_pk(id: $trailblazer_id) {
    id
    description
    healthcheck_info
    name
    status
    tags
    TrailBlazerSettings {
      trailblazer_mode
      debug
    }
    TrailBlazerIdentities(where: {deleted: {_eq: false}}) {
      trailblazer_id
      identity_id
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

    def GetTrailBlazerAndIdentities(self, trailblazer_id: int):
        query = gql(self._GetTrailBlazerAndIdentitiesQuery)
        variables = {
            "trailblazer_id": trailblazer_id,
        }
        operation_name = "GetTrailBlazerAndIdentities"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

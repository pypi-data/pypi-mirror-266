from gql import gql
from typing import Sequence

class getMethods:

    _GetTrailBlazerApiKeyQuery = """
    query GetTrailBlazerApiKey($trailblazer_id: Int!) {
  TrailBlazerApiKeys(where: {trailblazer_id: {_eq: $trailblazer_id}}) {
    trailblazer_id
    id
    api_key
    TrailBlazer {
      id
      org_id
      status
    }
  }
}
    """

    def GetTrailBlazerApiKey(self, trailblazer_id: int):
        query = gql(self._GetTrailBlazerApiKeyQuery)
        variables = {
            "trailblazer_id": trailblazer_id,
        }
        operation_name = "GetTrailBlazerApiKey"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

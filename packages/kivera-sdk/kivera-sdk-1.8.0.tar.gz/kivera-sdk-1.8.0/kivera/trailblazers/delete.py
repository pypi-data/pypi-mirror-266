from gql import gql
from typing import Sequence

class deleteMethods:

    _DeleteTrailBlazerQuery = """
    mutation DeleteTrailBlazer($id: Int!) {
  update_TrailBlazers_by_pk(pk_columns: {id: $id}, _set: {deleted: true, status: "DELETING"}) {
    id
    deleted
  }
  update_TrailBlazerIdentities(where: {trailblazer_id: {_eq: $id}}, _set: {deleted: true}) {
    affected_rows
  }
}
    """

    def DeleteTrailBlazer(self, id: int):
        query = gql(self._DeleteTrailBlazerQuery)
        variables = {
            "id": id,
        }
        operation_name = "DeleteTrailBlazer"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

from gql import gql
from typing import Sequence

class getMethods:

    _GetNotificationDestinationV2Query = """
    query GetNotificationDestinationV2($id: String!) {
  NotificationDestinations_by_pk(id: $id) {
    id
    name
    destination_type
    org_id
    config
    description
  }
}
    """

    def GetNotificationDestinationV2(self, id: str):
        query = gql(self._GetNotificationDestinationV2Query)
        variables = {
            "id": id,
        }
        operation_name = "GetNotificationDestinationV2"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetNotificationDestinationsQuery = """
    query GetNotificationDestinations ($id: String!) {
  NotificationDestinations(where: {id: {_eq: $id}}) {
    id
    name
    destination_type
    org_id
    config
    description
  }
}
    """

    def GetNotificationDestinations(self, id: str):
        query = gql(self._GetNotificationDestinationsQuery)
        variables = {
            "id": id,
        }
        operation_name = "GetNotificationDestinations"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

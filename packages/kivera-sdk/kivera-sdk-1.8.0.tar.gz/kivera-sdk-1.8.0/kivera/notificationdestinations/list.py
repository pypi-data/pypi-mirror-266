from gql import gql
from typing import Sequence

class listMethods:

    _ListNotificationDestinationsQuery = """
    query ListNotificationDestinations {
  NotificationDestinations {
    id
    name
    destination_type
    org_id
    config
    description
    NotificationMonitorDestinations {
      id
      monitor_id
    }
  }
}
    """

    def ListNotificationDestinations(self):
        query = gql(self._ListNotificationDestinationsQuery)
        variables = {
        }
        operation_name = "ListNotificationDestinations"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

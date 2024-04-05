from gql import gql
from typing import Sequence

class listMethods:

    _ListNotificationMonitorsQuery = """
    query ListNotificationMonitors {
  NotificationMonitors {
    id
    name
    description
    org_id
    enabled
    query_parameters
    interval
    severity
    NotificationMonitorDestinations {
      destination_id
    }
  }
}
    """

    def ListNotificationMonitors(self):
        query = gql(self._ListNotificationMonitorsQuery)
        variables = {
        }
        operation_name = "ListNotificationMonitors"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _ListNotificationMonitorsFullQuery = """
    query ListNotificationMonitorsFull {
  NotificationMonitors {
    id
    name
    description
    org_id
    enabled
    query_parameters
    interval
    severity
    NotificationMonitorDestinations {
      NotificationDestination {
        id
        destination_type
        name
        description
        config
      }
    }
  }
}
    """

    def ListNotificationMonitorsFull(self):
        query = gql(self._ListNotificationMonitorsFullQuery)
        variables = {
        }
        operation_name = "ListNotificationMonitorsFull"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

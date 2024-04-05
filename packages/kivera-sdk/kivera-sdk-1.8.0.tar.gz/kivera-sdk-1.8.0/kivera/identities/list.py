from gql import gql
from typing import Sequence

class listMethods:

    _ListIdentitiesQuery = """
    query ListIdentities {
  Identities(where: {status: {_eq: true}}) {
    config
    description
    name
    organization_id
    status
    tags
    type_id
    id
    identity_type
    Counters_aggregate {
      aggregate {
        sum {
          counter_accepts
          counter_denials
          counter_notifies
          counter_total_request
        }
      }
    }
    IdentityType {
      identity_type
    }
    IdentityProfiles_aggregate(where: {deleted: {_eq: false}})  {
      aggregate {
        count
      }
    }
    IdentityProfiles(where: {deleted: {_eq: false}}) {
      profile_id
      Profile  {
        ProfileRules_aggregate(where: {deleted: {_eq: false}}) {
          aggregate {
            count
          }
        }
      }
    }
  }
}
    """

    def ListIdentities(self):
        query = gql(self._ListIdentitiesQuery)
        variables = {
        }
        operation_name = "ListIdentities"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

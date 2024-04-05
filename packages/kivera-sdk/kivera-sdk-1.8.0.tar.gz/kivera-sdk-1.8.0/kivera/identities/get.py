from gql import gql
from typing import Sequence

class getMethods:

    _GetIdentityQuery = """
    query GetIdentity($id: Int!) {
  Identities(where: {id: {_eq: $id}, status: {_eq: true}}) {
    config
    description
    name
    organization_id
    status
    tags
    type_id
    id
    identity_type
    IdentityProfiles(where: {deleted: {_eq: false}}) {
      identity_id
      profile_id
      Profile  {
        name
        description
        ProfileRules_aggregate(where: {deleted: {_eq: false}}) {
          aggregate {
            count
          }
        }
      }
    }
    IdentityType {
      identity_type
      id
      config
    }
    ProxyIdentities(where: {Proxy: {status: {_neq: "DELETED"}, _and: {status: {_neq: "DELETING"}}}}) {
      identity_id
      proxy_id
      Proxy {
        name
      }
    }
    ProxySettings(where: {Proxy: {status: {_neq: "DELETED"}, _and: {status: {_neq: "DELETING"}}}}) {
      proxy_id
      Proxy {
        name
      }
      default_identity_id
    }
    AwsTenants {
      id
      account_id
      unique_id
      verified
      identity_id
      provider_id
      role_arn
    }
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
    IdentityProfiles_aggregate(where: {deleted: {_eq: false}})  {
      aggregate {
        count
      }
    }
  }
  Profiles_aggregate {
    aggregate {
      count
    }
  }
}
    """

    def GetIdentity(self, id: int):
        query = gql(self._GetIdentityQuery)
        variables = {
            "id": id,
        }
        operation_name = "GetIdentity"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetIdentityConfigQuery = """
    query GetIdentityConfig {
  Organizations {
    OrganizationPolicyFunction {
    	id
      organization_id
      function
    }
  }
  Identities {
    id
    status
    IdentityType {
      identity_type
      id
      config
    }
    IdentityProfiles(where: {deleted: {_eq: false}}) {
      Profile {
        ...ProfileFields
      }
    }
  }
}

fragment ProfileFields on Profiles {
  organization_id
  name
  id
  description
  tags
  ProfileRules(
    where: { deleted: { _eq: false } }
    order_by: { Rule: { dependencies_enabled: desc } }
  ) {
    Rule {
      id
      description
      config
      policy
      service_id
      type_id
      enable_cfn_scan
      enforce
      log_request_body
      dependencies_enabled
      tags
      ruleDependenciesByRuleId(where: { deleted: { _eq: false } }) {
        id
        dependent_rule_id
        rule_id
        Rule {
          id
          description
          config
          policy
          service_id
          type_id
          enable_cfn_scan
          enforce
          log_request_body
          dependencies_enabled
          tags
          Service {
            GlobalService {
              name
              Provider {
                name
              }
            }
          }
          RuleParameters(where: { deleted: { _eq: false } }) {
            parameter_name
            parameter_value
          }
        }
        RuleDependenciesResources {
          id
          identity_id
          locked
          resource_id
          rule_dependencies_id
          RuleDependency {
            rule_id
            dependent_rule_id
          }
        }
      }
      Service {
        GlobalService {
          name
          Provider {
            name
          }
        }
      }
      RuleParameters(where: { deleted: { _eq: false } }) {
        parameter_name
        parameter_value
      }
    }
  }
}
    """

    def GetIdentityConfig(self):
        query = gql(self._GetIdentityConfigQuery)
        variables = {
        }
        operation_name = "GetIdentityConfig"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetIdentityConfigV4Query = """
    query GetIdentityConfigV4 {
  Organizations {
    OrganizationPolicyFunction {
      id
      organization_id
      function
    }
  }
  Identities {
    id
    status
    IdentityType {
      identity_type
      id
      config
    }
    IdentityProfiles(where: {deleted: {_eq: false}}) {
      Profile {
        ...ProfileFieldsV4
      }
    }
  }
}

fragment ProfileFieldsV4 on Profiles {
  organization_id
  name
  id
  description
  tags
  ProfileRules(
    where: { deleted: { _eq: false } }
    order_by: { Rule: { dependencies_enabled: desc } }
  ) {
    Rule {
      id
      description
      config
      service_id
      type_id
      enable_cfn_scan
      enforce
      log_request_body
      dependencies_enabled
      tags
      risk_rating
      policy
      ruleDependenciesByRuleId(where: { deleted: { _eq: false } }) {
        id
        dependent_rule_id
        rule_id
        Rule {
          id
          description
          config
          service_id
          type_id
          enable_cfn_scan
          enforce
          log_request_body
          dependencies_enabled
          tags
          policy
          Service {
            GlobalService {
              name
              Provider {
                name
              }
            }
          }
          RuleParameters(where: { deleted: { _eq: false } }) {
            parameter_name
            parameter_value
          }
        }
        RuleDependenciesResources {
          id
          identity_id
          locked
          resource_id
          rule_dependencies_id
          RuleDependency {
            rule_id
            dependent_rule_id
          }
        }
      }
      Service {
        GlobalService {
          name
          Provider {
            name
          }
        }
      }
      RuleParameters(where: { deleted: { _eq: false } }) {
        parameter_name
        parameter_value
      }
    }
  }
}
    """

    def GetIdentityConfigV4(self):
        query = gql(self._GetIdentityConfigV4Query)
        variables = {
        }
        operation_name = "GetIdentityConfigV4"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

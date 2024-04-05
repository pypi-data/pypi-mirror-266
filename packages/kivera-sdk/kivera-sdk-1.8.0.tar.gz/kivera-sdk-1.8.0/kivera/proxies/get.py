from gql import gql
from typing import Sequence

class getMethods:

    _GetProxyQuery = """
    query GetProxy($proxy_id: Int!) {
  Proxies_by_pk(id: $proxy_id) {
    description
    id
    last_healthcheck_time
    name
    organization_id
    status
  }
}
    """

    def GetProxy(self, proxy_id: int):
        query = gql(self._GetProxyQuery)
        variables = {
            "proxy_id": proxy_id,
        }
        operation_name = "GetProxy"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetProxyConfigQuery = """
    query GetProxyConfig {
  Identities(
    where: {
      _or: [
        { ProxyIdentities: { deleted: { _eq: false } } }
        { ProxySettings: { default_identity_id: { _is_null: false } } }
      ]
    }
  ) {
    organization_id
    name
    id
    description
    config
    status
    tags
    IdentityType {
      identity_type
      id
      config
    }
    IdentityProfiles(where: { deleted: { _eq: false } }) {
      Profile {
        ...ProfileFields
      }
    }
  }
  Proxies {
    organization_id
    status
    id
    description
    name
    tags
    ProxyApiKeys {
      id
    }
    ProxyProviders(where: { enabled: { _eq: true } }) {
      provider_autoupdate
      ProviderVersion {
        version_name
        created
        hash
      }
      Provider {
        name
        ProviderVersions(order_by: { created: desc }, limit: 1) {
          version_name
          created
          hash
        }
        GlobalServices(
          where: { Services: { inspection: { _neq: "disabled" } } }
        ) {
          name
          Services {
            inspection
          }
        }
      }
    }
  }
  ProxySettings {
    debug
    default_mode
    proxy_mode
    allow_noncloud_traffic
    default_identity_id
    Identity {
      tags
      name
      id
      description
      IdentityType {
        id
        identity_type
      }
    }
  }
  Counters {
    counter_total_request
    counter_notifies
    counter_denials
    counter_accepts
  }
  Providers {
    name
    id
    ProviderDomains {
      domain_regex
    }
  }
  Organizations {
    technical_contact
    plan_id
    max_total_request_count
    id
    domain
    company_name
    billing_contact
    OrganizationPolicyFunction {
      id
      name
      function
    }
  }
  Profiles {
    organization_id
    name
    id
    description
    tags
  }
  GlobalPolicyFunctions(order_by: { id: asc }) {
    id
    name
    function
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

    def GetProxyConfig(self):
        query = gql(self._GetProxyConfigQuery)
        variables = {
        }
        operation_name = "GetProxyConfig"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetProxyConfigV4Query = """
    query GetProxyConfigV4 {
  Identities(
    where: {
      _or: [
        { ProxyIdentities: { deleted: { _eq: false } } }
        { ProxySettings: { default_identity_id: { _is_null: false } } }
      ]
    }
  ) {
    organization_id
    name
    id
    description
    config
    status
    tags
    identity_type
    IdentityProfiles(where: { deleted: { _eq: false } }) {
      Profile {
        ...ProfileFieldsV4
      }
    }
  }
  Proxies {
    organization_id
    status
    id
    description
    name
    tags
    ProxyApiKeys {
      id
    }
    ProxyProviders(where: { enabled: { _eq: true } }) {
      provider_id
      provider_autoupdate
      ProviderVersion {
        version_name
        created
        hash
      }
      Provider {
        name
        ProviderVersions(order_by: { created: desc }, limit: 1) {
          version_name
          created
          hash
        }
        GlobalServices(
          where: { Services: { inspection: { _neq: "disabled" } } }
        ) {
          name
          Services {
            inspection
          }
        }
      }
    }
  }
  ProxySettings {
    debug
    default_mode
    learning_mode
    proxy_mode
    allow_noncloud_traffic
    default_identity_id
    Identity {
      tags
      name
      id
      description
      IdentityType {
        id
        identity_type
      }
    }
  }
  Counters {
    counter_total_request
    counter_notifies
    counter_denials
    counter_accepts
  }
  Providers {
    name
    id
    ProviderDomains {
      domain_regex
    }
  }
  Organizations {
    technical_contact
    plan_id
    max_total_request_count
    id
    domain
    company_name
    billing_contact
    OrganizationPolicyFunction {
      id
      name
      function
    }
    CloudTenants {
      id
      name
      Provider {
        name
      }
      tenant_structure
    }
  }
  Profiles {
    organization_id
    name
    id
    description
    tags
  }
  GlobalPolicyFunctions(order_by: { id: asc }) {
    id
    name
    function
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

    def GetProxyConfigV4(self):
        query = gql(self._GetProxyConfigV4Query)
        variables = {
        }
        operation_name = "GetProxyConfigV4"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetProxyDetailsQuery = """
    query GetProxyDetails($proxy_id: Int!) {
  Proxies_by_pk(id: $proxy_id) {
    description
    id
    last_healthcheck_time
    name
    organization_id
    status
    tags
    ProxySettings {
      id
      debug
      default_identity_id
      proxy_id
      proxy_mode
      learning_mode
      default_mode
      allow_noncloud_traffic
      Identity {
        id
        name
        description
        identity_type
        IdentityType {
          id
          identity_type
        }
      }
    }
    ProxyIdentities(where: { deleted: { _eq: false } }) {
      identity_id
      Identity {
        name
        description
        identity_type
        IdentityType {
          id
          identity_type
        }
      }
    }
    ProxyProviders {
      id
      provider_id
      proxy_id
      enabled
      Provider {
        name
      }
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
    ProxyDeployments {
      id
      config
      created_by_user_id
      date_created
      User {
        given_name
        family_name
        id
        email
      }
      config_version
      status
      proxy_id
      date_modified
      actioned_by_user_id
    }
  }
  Identities_aggregate {
    aggregate {
      count
    }
  }
}
    """

    def GetProxyDetails(self, proxy_id: int):
        query = gql(self._GetProxyDetailsQuery)
        variables = {
            "proxy_id": proxy_id,
        }
        operation_name = "GetProxyDetails"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetProxyIDQuery = """
    query GetProxyID($proxy_name: String!) {
  Proxies(where: { name: { _eq: $proxy_name } }) {
    description
    id
    last_healthcheck_time
    name
    organization_id
    status
  }
}
    """

    def GetProxyID(self, proxy_name: str):
        query = gql(self._GetProxyIDQuery)
        variables = {
            "proxy_name": proxy_name,
        }
        operation_name = "GetProxyID"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetProxyV2Query = """
    query GetProxyV2($proxy_id: Int!) {
  Proxies_by_pk(id: $proxy_id) {
    description
    id
    last_healthcheck_time
    name
    organization_id
    status
    tags
    ProxySettings {
      allow_noncloud_traffic
      debug
      default_mode
      proxy_mode
    }
    ProxyProviders {
      id
      provider_id
      enabled
      provider_autoupdate
      provider_version_id
    }
  }
}
    """

    def GetProxyV2(self, proxy_id: int):
        query = gql(self._GetProxyV2Query)
        variables = {
            "proxy_id": proxy_id,
        }
        operation_name = "GetProxyV2"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

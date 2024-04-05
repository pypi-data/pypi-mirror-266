from gql import gql
from typing import Sequence

class getMethods:

    _GetLatestProxyDeploymentConfigQuery = """
    query GetLatestProxyDeploymentConfig {
  ProxyDeployments(
    order_by: { date_created: desc }
    limit: 1
    where: { status: { _eq: "APPROVED" } }
  ) {
    id
    created_by_user_id
    date_created
    config_version
    status
    proxy_id
    date_modified
    actioned_by_user_id
  }
}
    """

    def GetLatestProxyDeploymentConfig(self):
        query = gql(self._GetLatestProxyDeploymentConfigQuery)
        variables = {
        }
        operation_name = "GetLatestProxyDeploymentConfig"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetProxyDeploymentConfigQuery = """
    query GetProxyDeploymentConfig($id: Int!) {
  ProxyDeployments_by_pk(id: $id) {
    config
  }
}
    """

    def GetProxyDeploymentConfig(self, id: int):
        query = gql(self._GetProxyDeploymentConfigQuery)
        variables = {
            "id": id,
        }
        operation_name = "GetProxyDeploymentConfig"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetProxyDeploymentConfigV1Query = """
    query GetProxyDeploymentConfigV1($proxy_id: Int!) {
  Identities(
    where: {
      _or: [
        {
          ProxyIdentities: {
            proxy_id: { _eq: $proxy_id }
            deleted: { _eq: false }
          }
        }
        {
          ProxySettings: {
            proxy_id: { _eq: $proxy_id }
            default_identity_id: { _is_null: false }
          }
        }
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
        ...ProxyDeploymentProfileFields
      }
    }
  }
  Proxies(where: { id: { _eq: $proxy_id } }) {
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
  ProxySettings(where: { proxy_id: { _eq: $proxy_id } }) {
    debug
    default_mode
    proxy_mode
    allow_noncloud_traffic
    default_identity_id
    Identity {
      tags
      name
      id
    }
  }
  Counters(where: { proxy_id: { _eq: $proxy_id } }) {
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
  Organizations(where: { Proxies: { id: { _eq: $proxy_id } } }) {
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
  Profiles(
    where: {
      IdentityProfiles: {
        Identity: {
          _or: [
            {
              ProxyIdentities: {
                proxy_id: { _eq: $proxy_id }
                deleted: { _eq: false }
              }
            }
            {
              ProxySettings: {
                proxy_id: { _eq: $proxy_id }
                default_identity_id: { _is_null: false }
              }
            }
          ]
        }
      }
    }
  ) {
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

fragment ProxyDeploymentProfileFields on Profiles {
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

    def GetProxyDeploymentConfigV1(self, proxy_id: int):
        query = gql(self._GetProxyDeploymentConfigV1Query)
        variables = {
            "proxy_id": proxy_id,
        }
        operation_name = "GetProxyDeploymentConfigV1"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetProxyDeploymentConfigV1_4Query = """
    query GetProxyDeploymentConfigV1_4($proxy_id: Int!) {
  Identities(
    where: {
      _or: [
        {
          ProxyIdentities: {
            proxy_id: { _eq: $proxy_id }
            deleted: { _eq: false }
          }
        }
        {
          ProxySettings: {
            proxy_id: { _eq: $proxy_id }
            default_identity_id: { _is_null: false }
          }
        }
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
        ...ProxyDeploymentProfileFieldsV1_4
      }
    }
  }
  Proxies(where: { id: { _eq: $proxy_id } }) {
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
  ProxySettings(where: { proxy_id: { _eq: $proxy_id } }) {
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
  Counters(where: { proxy_id: { _eq: $proxy_id } }) {
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
  Organizations(where: { Proxies: { id: { _eq: $proxy_id } } }) {
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
      Provider {
        name
      }
      tenant_structure
    }
  }
  Profiles(
    where: {
      IdentityProfiles: {
        Identity: {
          _or: [
            {
              ProxyIdentities: {
                proxy_id: { _eq: $proxy_id }
                deleted: { _eq: false }
              }
            }
            {
              ProxySettings: {
                proxy_id: { _eq: $proxy_id }
                default_identity_id: { _is_null: false }
              }
            }
          ]
        }
      }
    }
  ) {
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

fragment ProxyDeploymentProfileFieldsV1_4 on Profiles {
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

    def GetProxyDeploymentConfigV1_4(self, proxy_id: int):
        query = gql(self._GetProxyDeploymentConfigV1_4Query)
        variables = {
            "proxy_id": proxy_id,
        }
        operation_name = "GetProxyDeploymentConfigV1_4"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

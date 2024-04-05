from gql import gql
from typing import Sequence

class updateMethods:

    _UpdateIdentityQuery = """
    mutation UpdateIdentity($id: Int!, $description: String!, $tags: jsonb!, $config: jsonb!, $identity_type: identity_type!, $profiles: [IdentityProfiles_insert_input!] = []) {
  update_Identities(
    where: {id: {_eq: $id}},
    _set: {
      description: $description,
      config: $config,
      tags: $tags,
      identity_type: $identity_type
  }) {
    returning {
      id
      name
      organization_id
      status
      type_id
      tags
      description
      config
    }
  }
  insert_IdentityProfiles(objects: $profiles, on_conflict: {constraint: identityprofiles_uniq_key, update_columns: [profile_id,deleted]}) {
    returning {
      id
      profile_id
    }
  }
}
    """

    def UpdateIdentity(self, id: int, description: str, tags: dict, config: dict, identity_type: dict, profiles: Sequence[dict] = None):
        query = gql(self._UpdateIdentityQuery)
        variables = {
            "id": id,
            "description": description,
            "tags": tags,
            "config": config,
            "identity_type": identity_type,
            "profiles": profiles,
        }
        operation_name = "UpdateIdentity"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

"""resources.py."""

from typing import List, Optional

from strangeworks_core.platform.gql import Operation
from strangeworks_core.types.resource import Resource

from strangeworks.platform.gql import SDKAPI

_get_op = Operation(
    query="""
        query sdk_get_resources {
            workspace  {
                resources {
                    edges {
                        node {
                            slug
                            isDeleted
                            status
                            product {
                                slug
                                name
                            }
                        }
                    }
                }
            }
        }
    """
)


def get(
    client: SDKAPI,
    resource_slug: Optional[str] = None,
) -> Optional[List[Resource]]:
    """Retrieve a list of available resources.

    Parameters
    ----------
    resource_slug: Optional[str]
        If supplied, only the resource whose slug matches will be returned. Defaults to
        None.

    Return
    ------
    Optional[List[Resource]]
        List of resources or None if workspace has no resources configured.
    """
    workspace = client.execute(_get_op).get("workspace")
    raw_list = workspace.get("resources")
    resources = (
        list(map(lambda x: Resource.from_dict(x.get("node")), raw_list.get("edges")))
        if raw_list
        else None
    )
    if resource_slug and resources:
        resources = [res for res in resources if res.slug == resource_slug]
    return resources

# Copyright The Cloud Custodian Authors.
# SPDX-License-Identifier: Apache-2.0

from c7n_azure.resources.arm import ArmResourceManager
from c7n_azure.provider import resources
from c7n.filters import Filter
from c7n.utils import type_schema

@resources.register('front-door')
class FrontDoor(ArmResourceManager):
    """Azure Front Door Resource

    :example:

    This policy will find all Front Doors

    .. code-block:: yaml

        policies:
          - name: all-front-doors
            resource: azure.front-door
    """

    class resource_type(ArmResourceManager.resource_type):
        doc_groups = ['Network']

        service = 'azure.mgmt.frontdoor'
        client = 'FrontDoorManagementClient'
        enum_spec = ('front_doors', 'list', None)
        default_report_fields = (
            'name',
            'location',
            'resourceGroup'
        )
        resource_type = 'Microsoft.Network/frontDoors'

@FrontDoor.filter_registry.register('waf')
class WebAppFirewallFilter(Filter):
    """Frontdoor check waf enabled on front door profiles for Classic_AzureFrontDoor

    :example:

    .. code-block:: yaml

        policies:
            name: test-frontdoor-waf
            resource: azure.front-door
            filters: 
              - type: waf
                link: None
            

    """
    schema = type_schema('waf',required=['value'],
            value={'type': 'string', 'enum': ['None', 'not None']})
    

    def process(self, resources, event=None):
        client = self.manager.get_client()
        matched = []
        for frontDoors in resources:
            for frontEndpoints in frontDoors['properties']['frontendEndpoints']:
                frontEndpoint = client.frontend_endpoints.get(
                    frontDoors['resourceGroup'], frontDoors['name'],frontEndpoints['name'])
                if frontEndpoint.web_application_firewall_policy_link is self.data.get('value'):
                    matched.append(frontDoors)
        return matched

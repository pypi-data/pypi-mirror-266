# -*- coding: utf-8 -*-
# Copyright © 2021-24 Wacom. All rights reserved.
from typing import List, Dict

import requests
from requests import Response

from knowledge.services import DEFAULT_TIMEOUT
from knowledge.services.base import WacomServiceAPIClient, USER_AGENT_HEADER_FLAG, \
    CONTENT_TYPE_HEADER_FLAG, handle_error
from knowledge.services.graph import AUTHORIZATION_HEADER_FLAG


class TenantManagementServiceAPI(WacomServiceAPIClient):
    """
    Tenant Management Service API
    -----------------------------

    Functionality:
        - List all tenants
        - Create tenants

    This is service is used to manage tenants. Only admins can use this service, as it requires the secret key for
    tenant administration.

    Parameters
    ----------
    tenant_token: str
        Tenant Management token
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint
    """

    TENANT_ENDPOINT: str = 'tenant'
    USER_DETAILS_ENDPOINT: str = f'{WacomServiceAPIClient.USER_ENDPOINT}/users'

    def __init__(self, tenant_token: str, service_url: str = WacomServiceAPIClient.SERVICE_URL,
                 service_endpoint: str = 'graph/v1'):
        self.__tenant_management_token: str = tenant_token
        super().__init__("TenantManagementServiceAPI", service_url=service_url, service_endpoint=service_endpoint)

    @property
    def tenant_management_token(self) -> str:
        """Tenant Management token."""
        return self.__tenant_management_token

    @tenant_management_token.setter
    def tenant_management_token(self, value: str):
        self.__tenant_management_token = value

    # ------------------------------------------ Tenants handling ------------------------------------------------------

    def create_tenant(self, name: str) -> Dict[str, str]:
        """
        Creates a tenant.

        Parameters
        ----------
        name: str -
            Name of the tenant

        Returns
        -------
        tenant_dict: Dict[str, str]
            Newly created tenant structure.
            >>>     {
            >>>       "id": "<Tenant-ID>",
            >>>       "apiKey": "<Tenant-API-Key>",
            >>>       "name": "<Tenant-Name>"
            >>>    }

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f'{self.service_base_url}{TenantManagementServiceAPI.TENANT_ENDPOINT}'
        headers: dict = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f'Bearer {self.__tenant_management_token}',
            CONTENT_TYPE_HEADER_FLAG: 'application/json'
        }
        payload: dict = {
            'name': name
        }
        response: Response = requests.post(url, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT,
                                           verify=self.verify_calls)
        if response.ok:
            return response.json()
        raise handle_error("Creation of tenant failed.", response)

    def listing_tenant(self) -> List[Dict[str, str]]:
        """
        Listing all tenants configured for this instance.

        Returns
        -------
        tenants:  List[Dict[str, str]]
            List of tenants:
            >>> [
            >>>     {
            >>>        "id": "<Tenant-ID>",
            >>>        "ontologyName": "<Name-Of-Ontology>",
            >>>        "ontologyVersion": "<Version-Of-Ontology>",
            >>>        "isLocked": "<Lock-Flag>",
            >>>        "name": "<Tenant-Name>"
            >>>     },
            >>>     ...
            >>> ]
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f'{self.service_base_url}{TenantManagementServiceAPI.TENANT_ENDPOINT}'
        headers: dict = {
            USER_AGENT_HEADER_FLAG: self.user_agent,
            AUTHORIZATION_HEADER_FLAG: f'Bearer {self.__tenant_management_token}'
        }
        response: Response = requests.get(url, headers=headers, data={}, timeout=DEFAULT_TIMEOUT,
                                          verify=self.verify_calls)
        if response.ok:
            return response.json()
        raise handle_error("Listing of tenant failed.", response)

from typing import Any, Callable, Dict, List, Optional

import antimatter.client as openapi_client
from antimatter.client import DefaultApi
from antimatter.session_mixins.token import exec_with_token


class DomainMixin:
    """
    Session mixin defining CRUD functionality for domains, including peering.
    """

    def __init__(self, domain: str, client_func: Callable[[], DefaultApi], **kwargs):
        try:
            super().__init__(domain=domain, client_func=client_func, **kwargs)
        except TypeError:
            super().__init__()  # If this is last mixin, super() will be object()
        self._domain = domain
        self._client_func = client_func

    @exec_with_token
    def new_domain(self, admin_email: str) -> Dict[str, Any]:
        """
        Create a new domain with no default peer relationships.
        """
        return self._client_func().domain_add_new(
            new_domain=openapi_client.NewDomain(admin_email=admin_email),
        ).model_dump()

    @exec_with_token
    def new_peer_domain(
        self,
        import_alias_for_child: str,
        display_name_for_child: str,
        nicknames: Optional[List[str]] = None,
        import_alias_for_parent: Optional[str] = None,
        display_name_for_parent: Optional[str] = None,
        link_all: bool = True,
        link_identity_providers: bool = None,
        link_facts: bool = None,
        link_read_contexts: bool = None,
        link_write_contexts: bool = None,
        link_capabilities: bool = None,
        link_domain_policy: bool = None,
        link_capsule_access_log: bool = None,
        link_control_log: bool = None,
        link_capsule_manifest: bool = None,
    ) -> Dict[str, Any]:
        """
        Creates a new peer domain

        :param import_alias_for_child: The import alias for the child domain
        :param display_name_for_child: The display name for the child domain
        :param nicknames: The nicknames for the child domain
        :param import_alias_for_parent: The import alias for the parent domain
        :param display_name_for_parent: The display name for the parent domain
        :param link_all: Whether to link all capabilities
        :param link_identity_providers: Whether to link identity providers
        :param link_facts: Whether to link facts
        :param link_read_contexts: Whether to link read contexts
        :param link_write_contexts: Whether to link write contexts
        :param link_capabilities: Whether to link capabilities
        :param link_domain_policy: Whether to link domain policy
        :param link_capsule_access_log: Whether to link capsule access log
        :param link_control_log: Whether to link control log
        :param link_capsule_manifest: Whether to link capsule manifest

        :return: The new peer domain
        """
        return self._client_func().domain_create_peer_domain(
            domain_id=self._domain,
            create_peer_domain=openapi_client.CreatePeerDomain(
                import_alias_for_child=import_alias_for_child,
                display_name_for_child=display_name_for_child,
                nicknames=nicknames,
                import_alias_for_parent=import_alias_for_parent,
                display_name_for_parent=display_name_for_parent,
                link_all=link_all,
                link_identity_providers=link_identity_providers,
                link_facts=link_facts,
                link_read_contexts=link_read_contexts,
                link_write_contexts=link_write_contexts,
                link_capabilities=link_capabilities,
                link_domain_policy=link_domain_policy,
                link_capsule_access_log=link_capsule_access_log,
                link_control_log=link_control_log,
                link_capsule_manifest=link_capsule_manifest,
            )
        ).model_dump()

    @exec_with_token
    def get_peer(self, nickname: Optional[str] = None, alias: Optional[str] = None) -> str:
        """
        Retrieve the domain ID of a domain that is configured as a peer of this
        session's domain by using either its alias or one of its nicknames.

        :param nickname: The nickname for the peer domain
        :param alias: One of the aliases of the peer domain
        :return: The domain ID
        """
        return self._client_func().domain_get_peer(domain_id=self._domain, nickname=nickname, alias=alias).id

    @exec_with_token
    def list_peers(self):
        """
        Return a list of the peers of this session's domain.

        :return: The peer list, containing IDs and other information about the domains
        """
        return [p.model_dump() for p in self._client_func().domain_list_peers(domain_id=self._domain).peers]

    @exec_with_token
    def get_peer_config(
        self,
        peer_domain_id: Optional[str] = None,
        nickname: Optional[str] = None,
        alias: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get a peer configuration using one of the peer's domain ID, nickname, or
        alias.

        :param peer_domain_id: The domain ID of the peer
        :param nickname: The nickname for the peer domain
        :param alias: One of the aliases of the peer domain
        :return: The full peer configuration
        """
        if not peer_domain_id and (nickname or alias):
            peer_domain_id = self.get_peer(nickname=nickname, alias=alias)
        return self._client_func().domain_get_peer_config(
            domain_id=self._domain, peer_domain_id=peer_domain_id,
        ).model_dump()

    @exec_with_token
    def update_peer(
        self,
        display_name: str,
        peer_domain_id: Optional[str] = None,
        nickname: Optional[str] = None,
        alias: Optional[str] = None,
        export_identity_providers: Optional[List[str]] = None,
        export_all_identity_providers: Optional[bool] = None,
        export_facts: Optional[List[str]] = None,
        export_all_facts: Optional[bool] = None,
        export_read_contexts: Optional[List[str]] = None,
        export_all_read_contexts: Optional[bool] = None,
        export_write_contexts: Optional[List[str]] = None,
        export_all_write_contexts: Optional[bool] = None,
        export_capabilities: Optional[List[str]] = None,
        export_all_capabilities: Optional[bool] = None,
        export_domain_policy: Optional[bool] = None,
        export_capsule_access_log: Optional[bool] = None,
        export_control_log: Optional[bool] = None,
        export_capsule_manifest: Optional[bool] = None,
        export_billing: Optional[bool] = None,
        export_admin_contact: Optional[bool] = None,
        nicknames: Optional[List[str]] = None,
        import_alias: Optional[str] = None,
        forward_billing: Optional[bool] = None,
        forward_admin_communications: Optional[bool] = None,
        import_identity_providers: Optional[List[str]] = None,
        import_all_identity_providers: Optional[bool] = None,
        import_facts: Optional[List[str]] = None,
        import_all_facts: Optional[bool] = None,
        import_read_contexts: Optional[List[str]] = None,
        import_all_read_contexts: Optional[bool] = None,
        import_write_contexts: Optional[List[str]] = None,
        import_all_write_contexts: Optional[bool] = None,
        import_capabilities: Optional[List[str]] = None,
        import_all_capabilities: Optional[bool] = None,
        import_domain_policy: Optional[bool] = None,
        import_precedence: Optional[int] = None,
        import_capsule_access_log: Optional[bool] = None,
        import_control_log: Optional[bool] = None,
        import_capsule_manifest: Optional[bool] = None,
    ) -> None:
        """
        Create or update the configuration for this peer using one of the peer's
        domain ID, nickname, or alias. Please note, if the configuration already
        exists, it is updated to reflect the values in the request. This will
        include setting the fields to their default value if not supplied.

        :param display_name: The display name for the peer domain
        :param peer_domain_id: The domain ID of the peer
        :param nickname: The nickname for the peer domain
        :param alias: One of the aliases of the peer domain
        :param export_identity_providers: The identity providers to export
        :param export_all_identity_providers: Whether to export all identity providers
        :param export_facts: The facts to export
        :param export_all_facts: Whether to export all facts
        :param export_read_contexts: The read contexts to export
        :param export_all_read_contexts: Whether to export all read contexts
        :param export_write_contexts: The write contexts to export
        :param export_all_write_contexts: Whether to export all write contexts
        :param export_capabilities: The capabilities to export
        :param export_all_capabilities: Whether to export all capabilities
        :param export_domain_policy: Whether to export the domain policy
        :param export_capsule_access_log: Whether to export the capsule access log
        :param export_control_log: Whether to export the control log
        :param export_capsule_manifest: Whether to export the capsule manifest
        :param export_billing: Whether to export billing information
        :param export_admin_contact: Whether to export the admin contact
        :param nicknames: The nicknames for the peer domain
        :param import_alias: The import alias for the peer domain
        :param forward_billing: Whether to forward billing information
        :param forward_admin_communications: Whether to forward admin communications
        :param import_identity_providers: The identity providers to import
        :param import_all_identity_providers: Whether to import all identity providers
        :param import_facts: The facts to import
        :param import_all_facts: Whether to import all facts
        :param import_read_contexts: The read contexts to import
        :param import_all_read_contexts: Whether to import all read contexts
        :param import_write_contexts: The write contexts to import
        :param import_all_write_contexts: Whether to import all write contexts
        :param import_capabilities: The capabilities to import
        :param import_all_capabilities: Whether to import all capabilities
        :param import_domain_policy: Whether to import the domain policy
        :param import_precedence: The precedence of the import
        :param import_capsule_access_log: Whether to import the capsule access log
        :param import_control_log: Whether to import the control log
        :param import_capsule_manifest: Whether to import the capsule manifest
        """
        if not peer_domain_id and (nickname or alias):
            peer_domain_id = self.get_peer(nickname=nickname, alias=alias)
        self._client_func().domain_update_peer(
            domain_id=self._domain,
            peer_domain_id=peer_domain_id,
            domain_peer_config=openapi_client.DomainPeerConfig(
                display_name=display_name,
                export_identity_providers=export_identity_providers,
                export_all_identity_providers=export_all_identity_providers,
                export_facts=export_facts,
                export_all_facts=export_all_facts,
                export_read_contexts=export_read_contexts,
                export_all_read_contexts=export_all_read_contexts,
                export_write_contexts=export_write_contexts,
                export_all_write_contexts=export_all_write_contexts,
                export_capabilities=export_capabilities,
                export_all_capabilities=export_all_capabilities,
                export_domain_policy=export_domain_policy,
                export_capsule_access_log=export_capsule_access_log,
                export_control_log=export_control_log,
                export_capsule_manifest=export_capsule_manifest,
                export_billing=export_billing,
                export_admin_contact=export_admin_contact,
                nicknames=nicknames,
                import_alias=import_alias,
                forward_billing=forward_billing,
                forward_admin_communications=forward_admin_communications,
                import_identity_providers=import_identity_providers,
                import_all_identity_providers=import_all_identity_providers,
                import_facts=import_facts,
                import_all_facts=import_all_facts,
                import_read_contexts=import_read_contexts,
                import_all_read_contexts=import_all_read_contexts,
                import_write_contexts=import_write_contexts,
                import_all_write_contexts=import_all_write_contexts,
                import_capabilities=import_capabilities,
                import_all_capabilities=import_all_capabilities,
                import_domain_policy=import_domain_policy,
                import_precedence=import_precedence,
                import_capsule_access_log=import_capsule_access_log,
                import_control_log=import_control_log,
                import_capsule_manifest=import_capsule_manifest,
            )
        )

    @exec_with_token
    def delete_peer(
        self,
        peer_domain_id: Optional[str] = None,
        nickname: Optional[str] = None,
        alias: Optional[str] = None,
    ) -> None:
        """
        Remove the peering relationship with the given domain, using one of the
        peer's domain ID, nickname, or alias.

        :param peer_domain_id: The domain ID of the peer
        :param nickname: The nickname for the peer domain
        :param alias: One of the aliases of the peer domain
        """
        if not peer_domain_id and (nickname or alias):
            peer_domain_id = self.get_peer(nickname=nickname, alias=alias)
        self._client_func().domain_delete_peer(domain_id=self._domain, peer_domain_id=peer_domain_id)

    @exec_with_token
    def get_top_tags(self) -> List[str]:
        """
        Get domain tag info returns a list containing the top 100 tag names for the current session's domain.
        """
        res = self._client_func().domain_get_tag_info(
            domain_id=self._domain,
        )
        return [r.name for r in res.tags]

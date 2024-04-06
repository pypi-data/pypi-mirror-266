from typing import Any, Callable, Dict, List, Optional

import antimatter.client as openapi_client
from antimatter.client import DefaultApi
from antimatter.session_mixins.token import exec_with_token


class FactMixin:
    """
    Session mixin defining CRUD functionality for facts and fact types.

    :param domain: The domain to use for the session.
    :param client: The client to use for the session.
    """

    def __init__(self, domain: str, client_func: Callable[[], DefaultApi], **kwargs):
        try:
            super().__init__(domain=domain, client_func=client_func, **kwargs)
        except TypeError:
            super().__init__()  # If this is last mixin, super() will be object()
        self._domain = domain
        self._client_func = client_func

    @exec_with_token
    def list_fact_types(self):
        """
        Returns a list of fact types available for the current domain and auth
        """
        return [fact.model_dump() for fact in self._client_func().domain_list_fact_types(self._domain).fact_types]

    @exec_with_token
    def list_facts(self, fact_type: str):
        """
        Returns a list of facts for the given fact type
        """
        return [fact.model_dump() for fact in self._client_func().domain_list_facts(self._domain, fact_type=fact_type).facts]

    @exec_with_token
    def add_fact_type(
        self,
        name: str,
        description: str,
        arguments: Dict[str, str],
    ) -> None:
        """
        Upserts a fact type for the current domain and auth

        :param name: The "type name" for this fact, like "has_role"
        :param description: The human-readable description of the fact type
        :param arguments: Name:description argument pairs for the fact type
        """
        self._client_func().domain_put_fact_type(
            domain_id=self._domain,
            fact_type=name,
            new_fact_type_definition=openapi_client.NewFactTypeDefinition(
                description=description,
                arguments=[
                    openapi_client.NewFactTypeDefinitionArgumentsInner(name=name, description=desc)
                    for name, desc in arguments.items()
                ]
            ),
        )

    @exec_with_token
    def add_fact(
        self,
        fact_type: str,
        *arguments: str,
    ) -> Dict[str, Any]:
        """
        Upserts a fact for the current domain and auth

        :param fact_type: The name of the type of fact being added
        :param arguments: The fact arguments to add
        :return: The upserted fact
        """
        return self._client_func().domain_upsert_fact(
            domain_id=self._domain,
            fact_type=fact_type,
            new_fact=openapi_client.NewFact(arguments=arguments)
        ).model_dump()

    @exec_with_token
    def get_fact_type(self, fact_type: str) -> Dict[str, Any]:
        """
        Get the fact type details for the given fact type

        :param fact_type: The "type name" for this fact, like "has_role"
        :return: The fact type details
        """
        return self._client_func().domain_get_fact_type(
            domain_id=self._domain, fact_type=fact_type
        ).model_dump()

    @exec_with_token
    def get_fact(self, fact_type: str, fact_id: str) -> Dict[str, Any]:
        """
        Returns the fact details for the given fact type and name

        :param fact_type: The "type name" for this fact, like "has_role"
        :param fact_id: The ID for the fact to be retrieved
        :return: The fact details
        """
        return self._client_func().domain_get_fact_by_id(
            domain_id=self._domain, fact_type=fact_type, fact_id=fact_id
        ).model_dump()

    @exec_with_token
    def delete_fact_type(self, fact_type: str) -> None:
        """
        Delete a fact type AND ALL FACTS INSIDE IT.

        :param fact_type: The "type name" for this fact, like "has_role"
        """
        self._client_func().domain_delete_fact_type(domain_id=self._domain, fact_type=fact_type, confirm=fact_type)

    @exec_with_token
    def delete_fact(
        self,
        fact_type: str,
        fact_id: Optional[str] = None,
        arguments: Optional[List[str]] = None,
    ) -> None:
        """
        Delete a fact by ID or argument. One of 'fact_id' or 'arguments' must be
        provided. If 'fact_id' is provided, it will be used solely. If arguments
        are provided, each must fully match the name and/or arguments of the fact
        for it to be deleted.

        :param fact_type: The "type name" for this fact, like "has_role"
        :param fact_id: The ID for the fact to be deleted
        :param arguments: The arguments for the fact to be deleted
        """
        if fact_id is None and arguments is not None:
            for fact in self.list_facts(fact_type=fact_type):
                if arguments == fact.get("arguments", []):
                    self._client_func().domain_delete_fact_by_id(
                        domain_id=self._domain, fact_type=fact_type, fact_id=fact["id"])
        else:
            self._client_func().domain_delete_fact_by_id(domain_id=self._domain, fact_type=fact_type, fact_id=fact_id)

    @exec_with_token
    def delete_all_facts(self, fact_type: str) -> None:
        """
        Delete all the facts for the given fact type.

        :param fact_type: The "type name" for this fact, like "has_role"
        """
        for fact in self.list_facts(fact_type=fact_type):
            self._client_func().domain_delete_fact_by_id(
                domain_id=self._domain, fact_type=fact_type, fact_id=fact["id"])

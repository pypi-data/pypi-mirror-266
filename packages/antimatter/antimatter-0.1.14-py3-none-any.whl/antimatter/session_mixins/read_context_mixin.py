from typing import Any, Callable, Dict, List

from antimatter.builders import ReadContextBuilder, ReadContextRuleBuilder
from antimatter.client import DefaultApi
from antimatter.session_mixins.token import exec_with_token


class ReadContextMixin:
    """
    Session mixin defining CRUD functionality for read contexts.

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
    def add_read_context(
        self,
        name: str,
        builder: ReadContextBuilder
    ) -> None:
        """
        Upserts a read context for the current domain and auth

        :param name: The name of the read context to add or update
        :param builder: The builder containing read context configuration
        """
        self._client_func().domain_upsert_read_context(
            domain_id=self._domain, context_name=name, add_read_context=builder.build(),
        )

    @exec_with_token
    def list_read_context(self) -> List[Dict[str, Any]]:
        """
        Returns a list of read contexts available for the current domain and auth
        """
        return [ctx.model_dump() for ctx in self._client_func().domain_list_read_contexts(self._domain).read_contexts]

    @exec_with_token
    def describe_read_context(self, name: str) -> Dict[str, Any]:
        """
        Returns the read context with the given name for the current domain and auth

        :param name: The name of the read context to describe
        :return: The full details of the read context
        """
        return self._client_func().domain_get_read_context(self._domain, context_name=name).model_dump()

    @exec_with_token
    def delete_read_context(self, name: str) -> None:
        """
        Delete a read context. All configuration associated with this read
        context will also be deleted. Domain policy rules referencing this read
        context will be left as-is.

        :param name: The name of the read context to delete
        """
        self._client_func().domain_delete_read_context(domain_id=self._domain, context_name=name)

    @exec_with_token
    def list_read_context_rules(self, name: str) -> List[Dict[str, Any]]:
        """
        List all rules for the read context

        :param name: The name of the read context to list rules from
        :return: The list of read context rules
        """
        return [r.model_dump() for r in self._client_func().domain_get_read_context(self._domain, context_name=name).rules]

    @exec_with_token
    def add_read_context_rules(
        self,
        name: str,
        rule_builder: ReadContextRuleBuilder,
    ) -> str:
        """
        Adds rules to a read context

        :param name: The name of the read context to add rules to
        :param rule_builder: The builder containing rule configuration for the read context
        :return: The unique ID for the added read context rule
        """
        return self._client_func().domain_add_read_context_rule(
            domain_id=self._domain,
            context_name=name,
            new_read_context_config_rule=rule_builder.build()
        ).id

    @exec_with_token
    def update_read_context_rule(
        self,
        name: str,
        rule_id: str,
        rule_builder: ReadContextRuleBuilder,
    ) -> None:
        """
        Update a read context configuration rule. The rule must already exist.

        :param name: The name of the read context to update a rule for
        :param rule_id: The unique ID of the rule to update
        :param rule_builder: The builder containing rule configuration
        """
        self._client_func().domain_update_read_context_rule(
            domain_id=self._domain,
            context_name=name,
            rule_id=rule_id,
            new_read_context_config_rule=rule_builder.build()
        )

    @exec_with_token
    def delete_read_context_rule(
        self,
        name: str,
        rule_id: str,
    ) -> None:
        """
        Deletes a rule from a read context

        :param name: The name of the read context to delete a rule from
        :param rule_id: The unique ID of the rule to delete
        """
        self._client_func().domain_delete_read_context_rule(
            domain_id=self._domain,
            context_name=name,
            rule_id=rule_id,
        )

    @exec_with_token
    def delete_read_context_rules(self, name: str) -> None:
        """
        Deletes all the read context rules

        :param name: The name of the read context to delete all the rules from
        """
        for rule in self.list_read_context_rules(name):
            self._client_func().domain_delete_read_context_rule(
                domain_id=self._domain,
                context_name=name,
                rule_id=rule["id"],
            )

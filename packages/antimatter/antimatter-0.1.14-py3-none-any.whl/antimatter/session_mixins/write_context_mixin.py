from typing import Any, Callable, Dict, List

from antimatter.builders import WriteContextBuilder, WriteContextConfigurationBuilder, WriteContextRegexRuleBuilder
from antimatter.client import DefaultApi
from antimatter.session_mixins.token import exec_with_token


class WriteContextMixin:
    """
    Session mixin defining CRUD functionality for write contexts.

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
    def add_write_context(
        self,
        name: str,
        builder: WriteContextBuilder,
    ) -> None:
        """
        Upserts a write context for the current domain and auth

        :param name: The name of the write context to add or update
        :param builder: The builder containing write context configuration
        """
        self._client_func().domain_upsert_write_context(
            domain_id=self._domain, context_name=name, add_write_context=builder.build(),
        )

    @exec_with_token
    def list_write_context(self) -> List[Dict[str, Any]]:
        """
        Returns a list of write contexts available for the current domain and auth
        """
        return [ctx.model_dump() for ctx in self._client_func().domain_list_write_contexts(self._domain).write_contexts]

    @exec_with_token
    def describe_write_context(self, name: str) -> Dict[str, Any]:
        """
        Returns the write context with the given name for the current domain and auth

        :param name: The name of the write context to describe
        :return: The full details of the write context
        """
        return self._client_func().domain_describe_write_context(self._domain, context_name=name).model_dump()

    @exec_with_token
    def upsert_write_context_configuration(
        self,
        name: str,
        builder: WriteContextConfigurationBuilder,
    ) -> None:
        """
        Update a write context configuration. The write context must already exist.

        :param name: The name of the write context to update the configuration for
        :param builder: The builder containing write context configuration
        """
        self._client_func().domain_upsert_write_context_configuration(
            domain_id=self._domain,
            context_name=name,
            write_context_config_info=builder.build(),
        )

    @exec_with_token
    def delete_write_context(self, name: str) -> None:
        """
        Delete a write context. All configuration associated with this write
        context will also be deleted. Domain policy rules referencing this write
        context will be left as-is.

        :param name: The name of the write context to delete
        """
        self._client_func().domain_delete_write_context(domain_id=self._domain, context_name=name)

    @exec_with_token
    def list_write_context_regex_rules(self, context_name: str) -> List[Dict[str, Any]]:
        """
        List all regex rules for the write context.

        :param context_name: The name of the write context
        :return: The list of rules
        """
        return [rule.model_dump() for rule in self._client_func().domain_get_write_context_regex_rules(
            domain_id=self._domain,
            context_name=context_name,
        )]

    @exec_with_token
    def insert_write_context_regex_rule(
        self,
        context_name: str,
        builder: WriteContextRegexRuleBuilder,
    ) -> str:
        """
        Create a new regex rule for a write context.

        :param context_name: The name of the write context
        :param builder: The builder containing write context regex rule configuration
        """
        return self._client_func().domain_insert_write_context_regex_rule(
            domain_id=self._domain,
            context_name=context_name,
            write_context_regex_rule=builder.build(),
        ).rule_id

    @exec_with_token
    def delete_write_context_regex_rule(self, context_name: str, rule_id: str) -> None:
        """
        Delete a regex classifier rule for the context.

        :param context_name: The name of the write context
        :param rule_id: The ID of the rule to delete
        """
        self._client_func().domain_delete_write_context_regex_rule(
            domain_id=self._domain,
            context_name=context_name,
            rule_id=rule_id,
        )

    @exec_with_token
    def delete_write_context_regex_rules(self, context_name: str) -> None:
        """
        Delete the regex classifier rules for the context.

        :param context_name: The name of the write context
        """
        for rule in self.list_write_context_regex_rules(context_name=context_name):
            self._client_func().domain_delete_write_context_regex_rule(
                domain_id=self._domain,
                context_name=context_name,
                rule_id=rule["id"],
            )

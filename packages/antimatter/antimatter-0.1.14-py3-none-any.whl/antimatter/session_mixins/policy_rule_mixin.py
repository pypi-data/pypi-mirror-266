from typing import Any, Callable, Dict, List, Optional, Union

import antimatter.client as openapi_client
from antimatter.constants import domain_policy
from antimatter.builders.capability import CapabilityRulesBuilder
from antimatter.builders.fact_policy import FactPoliciesBuilder
from antimatter.client import DefaultApi
from antimatter.session_mixins.token import exec_with_token


class PolicyRuleMixin:
    """
    Session mixin defining policy rule CRUD functionality.

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
    def create_policy_rule(
            self,
            capability_rules: CapabilityRulesBuilder,
            path: str,
            operation: Union[str, domain_policy.Operation],
            result: Union[str, domain_policy.Result],
            priority: int,
            facts: Optional[FactPoliciesBuilder] = None,
            disabled: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a policy rule for the domain.

        :param capability_rules: Rules referring to domain identity capabilities. These rules are ANDed together
        :param facts: Assert the existence or nonexistence of facts that reference the capability rules.
                    These assertions will be ANDed together, and ANDed with the capability rules.
        :param path: The path this rule governs. May contain glob expressions (e.g. '*' and '**')
        :param operation: The operation to apply the policy to
        :param result: Whether to 'allow' or 'deny' the operation performed that matches this rule
        :param priority: The priority of this rule. Lower priority rules are evaluated first
        :param disabled: If this rule is disabled or not
        :return: A dictionary containing the created rule from the server
        """
        res = self._client_func().domain_create_policy_rule(
            domain_id=self._domain,
            domain_policy_rule=openapi_client.DomainPolicyRule(
                domain_identity=capability_rules.build(),
                facts=facts.build(),
                path=path,
                operation=domain_policy.Operation(operation).value,
                result=domain_policy.Result(result).value,
                priority=priority,
                disabled=disabled,
            ),
        )
        policy_rule = res.model_dump()
        return policy_rule

    @exec_with_token
    def delete_policy_rule(self, rule_id: str):
        """
        Delete a domain policy rule on the session's domain.

        :param rule_id: Identifier of the policy rule to delete
        """
        self._client_func().domain_delete_policy_rule(domain_id=self._domain, rule_id=rule_id)

    @exec_with_token
    def list_policy_rules(self):
        """
        Get the domain's policy rules.

        :return: A list of policy rules.
        """
        res = self._client_func().domain_list_policy_rules(domain_id=self._domain)
        policy_rules = []
        for rule in res.rules:
            policy_rules.append(rule.model_dump())
        return policy_rules

    @exec_with_token
    def update_policy_rule(
        self,
        rule_id: str,
        capability_rules: CapabilityRulesBuilder,
        facts: FactPoliciesBuilder,
        path: str,
        operation: Union[str, domain_policy.Operation],
        result: Union[str, domain_policy.Result],
        priority: int,
        disabled: bool = False,
    ) -> None:
        """
        Update a domain policy rule by ID.

        :param rule_id: The ID of the rule to update
        :param capability_rules: Rules referring to domain identity capabilities. These rules are ANDed together
        :param facts: Assert the existence or nonexistence of facts that reference the capability rules.
                    These assertions will be ANDed together, and ANDed with the capability rules.
        :param path: The path this rule governs. May contain glob expressions (e.g. '*' and '**')
        :param operation: The operation to apply the policy to
        :param result: Whether to 'allow' or 'deny' the operation performed that matches this rule
        :param priority: The priority of this rule. Lower priority rules are evaluated first
        :param disabled: If this rule is disabled or not
        """
        self._client_func().domain_update_policy_rule(
            domain_id=self._domain,
            rule_id=rule_id,
            domain_policy_rule=openapi_client.DomainPolicyRule(
                domain_identity=capability_rules.build(),
                facts=facts.build(),
                path=path,
                operation=domain_policy.Operation(operation).value,
                result=domain_policy.Result(result).value,
                priority=priority,
                disabled=disabled,
            ),
        )

    @exec_with_token
    def renumber_policy_rules(self) -> List[Dict[str, Any]]:
        """
        Re-assign rule priority numbers for the session's domain to integer multiples of 10

        :return: The full list of renumbered policy rules in this domain
        """
        res = self._client_func().domain_renumber_policy_rules(domain_id=self._domain)
        policy_rules = []
        for rule in res.rules:
            policy_rules.append(rule.model_dump())
        return policy_rules

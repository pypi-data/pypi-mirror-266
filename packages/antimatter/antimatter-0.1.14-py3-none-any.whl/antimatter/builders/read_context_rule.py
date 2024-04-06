from enum import Enum
from typing import List, Optional, Union

import antimatter.client as openapi_client
from antimatter.builders.fact_policy import FactOperator
from antimatter.constants import Action, Operator, Source, TokenFormat, TokenScope

class ReadContextRuleBuilder:
    """
    Builder class for creating a ReadContextConfigRule.
    """
    def __init__(self) -> None:
        """
        Initialize a new instance of ReadContextRuleBuilder.
        """
        self.rule = openapi_client.NewReadContextConfigRule(
            action=Action.Redact.value,
            priority=1,
            matchExpressions=[],
            facts=[],
        )

    def add_match_expression(
        self,
        source: Union[Source, str],
        key: str,
        operator: Union[Operator, str],
        values: Optional[List[str]] = None,
        value: Optional[str] = None,
    ) -> 'ReadContextRuleBuilder':
        """
        Add a match expression to the rule.

        :param source: The source of the match expression.
        :param key: The key of the match expression.
        :param operator: The operator of the match expression.
        :param values: The values of the match expression.
        :param value: The value of the match expression.
        :return: The builder instance.
        """
        match_expression = openapi_client.ReadContextRuleMatchExpressionsInner(
            source=Source(source).value, key=key, operator=Operator(operator).value, values=values, value=value)
        self.rule.match_expressions.append(match_expression)
        return self

    def set_action(self, action: Union[Action, str]) -> 'ReadContextRuleBuilder':
        """
        Set the action of the rule.

        :param action: The action of the rule.
        :return: The builder instance.
        """
        self.rule.action = Action(action).value
        return self

    def set_token_scope(self, token_scope: Union[TokenScope, str]) -> 'ReadContextRuleBuilder':
        """
        Set the token scope of the rule.

        :param token_scope: The token scope of the rule.
        :return: The builder instance.
        """
        self.rule.tokenScope = TokenScope(token_scope).value
        return self

    def set_token_format(self, token_format: Union[TokenFormat, str]) -> 'ReadContextRuleBuilder':
        """
        Set the token format of the rule.

        :param token_format: The token format of the rule.
        :return: The builder instance.
        """
        self.rule.tokenFormat = TokenFormat(token_format).value
        return self

    def set_priority(self, priority: int) -> 'ReadContextRuleBuilder':
        """
        Set the priority of the rule.

        :param priority: The priority of the rule.
        :return: The builder instance.
        """
        self.rule.priority = priority
        return self

    def add_fact(
        self,
        operator: Union[FactOperator, str],
        name: str,
        arguments_builder: 'ReadContextRuleFactArgumentBuilder' = None,
    ) -> 'ReadContextRuleBuilder':
        """
        Add a fact to the rule.

        :param operator: The operator of the fact.
        :param name: The name of the fact.
        :param arguments_builder: The arguments builder of the fact.
        :return: The builder instance.
        """
        fact = openapi_client.ReadContextRuleFactsInner(
            operator=FactOperator(operator).value,
            name=name,
            arguments=arguments_builder.build() if arguments_builder else []
        )
        self.rule.facts.append(fact)
        return self

    def build(self) -> openapi_client.NewReadContextConfigRule:
        """
        Build the rule.

        :return: The built rule.
        """
        return self.rule


class ReadContextRuleFactArgumentBuilder:
    """
    Builder class for creating a ReadContextConfigRuleFactArgument.
    """
    def __init__(self) -> None:
        """
        Initialize a new instance of ReadContextRuleFactArgumentBuilder.
        """
        self.arguments = []

    def add_argument(
        self, source: Union[Source, str], key: str = None, value: str = None,
    ) -> 'ReadContextRuleFactArgumentBuilder':
        """
        Add an argument to the fact.

        :param source: The source of the argument.
        :param key: The key of the argument.
        :param value: The value of the argument.
        :return: The builder instance.
        """
        self.arguments.append(openapi_client.ReadContextRuleFactsInnerArgumentsInner(
            key=key, value=value, source=Source(source).value,
        ))
        return self

    def build(self) -> List[openapi_client.ReadContextRuleFactsInnerArgumentsInner]:
        """
        Build the arguments.

        :return: The built arguments.
        """
        return self.arguments

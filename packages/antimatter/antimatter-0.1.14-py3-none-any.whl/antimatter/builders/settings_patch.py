from dataclasses import dataclass
from enum import Enum
from typing import Union

import antimatter.client as openapi_client
from antimatter.constants import PatchOperation

@dataclass
class SettingsPatchBuilder:
    """
    Builder class for creating a settings patch.

    :param path: The path of the patch.
    :param value: The value of the patch.
    :param operation: The operation of the patch.
    """
    path: str
    value: Union[bool, float, str]
    operation: Union[PatchOperation, str]

    def build(self) -> openapi_client.PatchRequestInner:
        """
        Build the patch.

        :return: The built patch.
        """
        self.operation = PatchOperation(self.operation)
        inner = None
        match self.operation:
            case PatchOperation.Add:
                inner = openapi_client.JSONPatchRequestAdd(
                    path=self.path,
                    value=openapi_client.JSONPatchRequestAddValue(self.value),
                    op=self.operation.Add.value,
                )
            case PatchOperation.Replace:
                inner = openapi_client.JSONPatchRequestReplace(
                    path=self.path,
                    value=openapi_client.JSONPatchRequestReplaceValue(self.value),
                    op=self.operation.Replace.value,
                )
            case PatchOperation.Test:
                inner = openapi_client.JSONPatchRequestTst(
                    path=self.path,
                    value=openapi_client.JSONPatchRequestTstValue(self.value),
                    op=self.operation.Test.value,
                )
            case PatchOperation.Remove:
                inner = openapi_client.JSONPatchRequestRemove(
                    path=self.path, op=self.operation.Remove.value,
                )
            case PatchOperation.Move:
                inner = openapi_client.JSONPatchRequestMove(
                    path=self.path, op=self.operation.Move.value,
                )
            case PatchOperation.Copy:
                inner = openapi_client.JSONPatchRequestCopy(
                    path=self.path, op=self.operation.Copy.value,
                )
        return openapi_client.PatchRequestInner(inner)

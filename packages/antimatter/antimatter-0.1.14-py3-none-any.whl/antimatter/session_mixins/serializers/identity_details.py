from typing import Any, Dict, Optional

import antimatter.client as openapi_client


def serialize_identity_provider_info_dict(model: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Serialize an identity provider info dictionary

    :param model: The identity provider info dictionary
    :return: The serialized dictionary
    """
    if model is None:
        return None
    ser = {k: v for k, v in model.items()}
    if "type" in model:
        ser["type"] = model["type"].value
    if "supported_principals" in model:
        ser["supported_principals"] = [p.value for p in model["supported_principals"]]
    if "details" in model:
        ser["details"] = model["details"]["actual_instance"]
    return ser


def serialize_identity_principal_details_dict(model: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Serialize an identity principal details dictionary

    :param model: The identity principal details dictionary
    :return: The serialized dictionary
    """
    if model is None:
        return None
    ser = {k: v for k, v in model.items()}
    if "details" in model:
        ser["details"] = model["details"]["actual_instance"]
    return ser

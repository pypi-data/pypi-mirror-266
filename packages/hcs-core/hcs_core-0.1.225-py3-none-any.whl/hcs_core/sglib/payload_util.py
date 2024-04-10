import json
import yaml
from .cli_options import get_org_id
from ..ctxp import CtxpException


def get_payload_with_defaults(file_arg, org: str):
    with file_arg:
        text = file_arg.read()

    try:
        payload = json.loads(text)
    except Exception as e1:
        try:
            payload = yaml.load(text)
        except Exception as e2:
            raise CtxpException("Invalid payload: " + str(e1))

    # Override org id, if specified explicitly on args.
    # Otherwise override using default, if not in payload.
    if org:
        payload["orgId"] = org
    else:
        if not payload.get("orgId"):
            payload["orgId"] = get_org_id()
    return payload

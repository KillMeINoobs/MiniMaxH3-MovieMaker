"""Small execution receipts; serial tokens never retain decoded tensors."""
from dataclasses import dataclass

from ...errors import fail


@dataclass(frozen=True)
class DecodeReceipt:
    manifest: dict
    origin: str


@dataclass(frozen=True)
class FinalizedToken:
    project_id: str
    plan_revision: int
    ordinal: int
    useful_end: int
    result_id: str
    generation_key: dict


def check_predecessor(token,*,project_id,plan_revision,ordinal,useful_start):
    if ordinal == 0:
        if token is not None: fail('PARTIAL_RESULT','The first window cannot use an unrelated predecessor.')
    elif (not isinstance(token,FinalizedToken) or token.project_id != project_id or
          token.plan_revision != plan_revision or token.ordinal != ordinal-1 or token.useful_end != useful_start):
        fail('PARTIAL_RESULT','Complete the exact previous useful window before starting this window.')
    return {'project_id':project_id,'plan_revision':plan_revision,'ordinal':ordinal,'useful_start':useful_start}

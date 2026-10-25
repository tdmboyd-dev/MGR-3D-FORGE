"""MGR Self-Repair Studio: bounded recoverable file-repair coordination.

The proposed fixes and validators here are trusted Python callbacks; this is
not a safe environment for running untrusted AI-generated arbitrary code.
"""

from dataclasses import dataclass

from .code_architect import WorkspaceFileJob


@dataclass(frozen=True)
class RepairOutcome:
    passed: bool
    attempts: int
    receipts: tuple[dict, ...]
    last_error: str | None = None


def repair_until_pass(workspace, *, propose, validate, max_attempts=3):
    """Apply only candidates that pass a trusted validator, reverting failures.

    `propose(attempt, last_error)` supplies file-change objects. Neither
    callback is safe to load from an untrusted repository without isolation.
    """
    if type(max_attempts) is not int or not 1 <= max_attempts <= 10:
        raise ValueError("max_attempts must be 1..10")
    runner = WorkspaceFileJob(workspace)
    receipts = []
    last_error = None
    for attempt in range(1,max_attempts+1):
        job_id=f"repair-{attempt}"
        changes=propose(attempt,last_error)
        receipt=runner.apply(job_id,changes)
        try:
            result=validate()
            if result is not True:
                raise ValueError("validation did not explicitly pass")
        except Exception as exc:
            last_error=f"{type(exc).__name__}: {exc}"
            runner.rollback(job_id)
            receipts.append({"attempt":attempt,"status":"REVERTED",
                             "reason":last_error,"changes":receipt["changes"]})
            continue
        receipts.append({"attempt":attempt,"status":"PASS",
                         "changes":receipt["changes"]})
        return RepairOutcome(True,attempt,tuple(receipts))
    return RepairOutcome(False,max_attempts,tuple(receipts),last_error)

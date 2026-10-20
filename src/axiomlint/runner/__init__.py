"""No runtime execution is authorized in the foundation."""


class ExecutionDisabled(RuntimeError):
    """WP-006 and its independent security review are not complete."""


def execute_subject(*args: object, **kwargs: object) -> None:
    raise ExecutionDisabled("Subject execution disabled: audited sandbox is unavailable")


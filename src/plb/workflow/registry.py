from plb.core.models import WorkflowStage

STAGE_ORDER: tuple[WorkflowStage, ...] = (
    WorkflowStage.DISCOVERY,
    WorkflowStage.DOMAIN,
    WorkflowStage.STATE,
    WorkflowStage.API,
    WorkflowStage.DESIGN,
    WorkflowStage.SLICE,
    WorkflowStage.GATES,
    WorkflowStage.IMPLEMENTATION,
)


def stage_names() -> list[str]:
    return [stage.value for stage in STAGE_ORDER]

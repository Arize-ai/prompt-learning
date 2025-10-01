from constants import CLINE_REPO_PATH, MATERIALIZED_REPOS_PATH
from cline_helpers import run_cline_for_instance
from pathlib import Path

def run_cline(instance: dict, idx: int, ruleset_text: str) -> dict:
    instance_id = instance["instance_id"]
    image_tag = f"sweb.eval.x86_64.{instance_id.lower()}:latest"

    # unique ports per job (avoid clashes)
    base = 27000 + idx * 10
    proto_port = base + 1
    hostbridge_port = base + 2

    result = {
        "instance_id": instance_id,
        "final_plan": "",
        "completion": "",
        "pass_or_fail": "",
    }

    out = run_cline_for_instance(
        instance_id=instance_id,
        image_tag=image_tag,
        cline_repo=Path(CLINE_REPO_PATH),
        workspaces_root=Path(MATERIALIZED_REPOS_PATH),
        task_text=instance["problem_statement"],
        host="127.0.0.1",
        proto_port=proto_port,
        hostbridge_port=hostbridge_port,
        wait_seconds=180,
        ruleset_text=ruleset_text,
    )

    result["final_plan"] = out.get("final_plan", "") 
    print(f"[{result['instance_id']}] CLINE done")

    return result
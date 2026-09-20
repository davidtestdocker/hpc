from pathlib import Path


TEMPLATE_PATH = Path(__file__).parent / "templates" / "jobset-mpi.yaml"
PLACEHOLDER = "__JOBSET_NAME__"


def render_mpi_jobset(job_id: str) -> str:
    jobset_name = f"mpi-{job_id}".lower()

    template = TEMPLATE_PATH.read_text()

    if PLACEHOLDER not in template:
        raise ValueError(f"Missing placeholder: {PLACEHOLDER}")

    return template.replace(PLACEHOLDER, jobset_name)

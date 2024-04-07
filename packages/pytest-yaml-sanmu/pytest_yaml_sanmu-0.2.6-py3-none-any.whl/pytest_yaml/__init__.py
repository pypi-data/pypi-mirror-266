from pathlib import Path

import yaml

dir_path = Path(__file__).parent

with open(dir_path / "yaml_case.schema.yaml", encoding="utf-8") as f:
    schema = yaml.safe_load(f)

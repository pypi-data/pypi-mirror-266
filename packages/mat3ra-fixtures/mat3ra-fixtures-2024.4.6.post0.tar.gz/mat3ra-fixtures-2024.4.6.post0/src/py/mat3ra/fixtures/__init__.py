from pathlib import Path

import yaml
from mat3ra.utils import object as object_utils


def get_content_by_reference_path(path_in_manifest_yaml: str) -> str:
    current_path = Path(__file__).parent

    with open(current_path.joinpath("./manifest.yml").as_posix(), "r") as file:
        manifest = yaml.safe_load(file)

    # When installed, the top-level path is the site-packages directory
    top_level_path = Path(__file__).parent  # / "../../../"

    path_from_top_level = object_utils.get(manifest, path_in_manifest_yaml).strip("/")

    full_path = top_level_path.joinpath(path_from_top_level).as_posix()

    with open(full_path, "r") as file:
        content = file.read()

    return content

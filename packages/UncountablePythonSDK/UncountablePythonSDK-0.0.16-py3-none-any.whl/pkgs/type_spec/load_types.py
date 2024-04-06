import os
from typing import Callable, Optional

import yaml
from shelljob import fs

from .builder import SpecBuilder
from .config import Config

ext_map = {
    ".ts": "typescript",
    ".py": "python",
}


def find_and_handle_files(
    root_folder: str, name_regex: str, handler: Callable[[str, str], None]
) -> None:
    for file_name in fs.find(root_folder, name_regex=name_regex, relative=True):
        with open(os.path.join(root_folder, file_name), encoding="utf-8") as file:
            handler(file_name, file.read())


def load_types(config: Config) -> Optional[SpecBuilder]:
    builder = SpecBuilder(api_endpoints=config.api_endpoint)

    def handle_builder_add(
        file_name: str, file_content: str, handler: Callable[[str, str, str], None]
    ) -> None:
        by_name, _ = os.path.splitext(file_name)
        name, ext = os.path.splitext(by_name)
        handler(ext_map[ext], name, file_content)

    for folder in config.type_spec_types:
        find_and_handle_files(
            folder,
            name_regex=".*\\.(ts|py)\\.part",
            handler=lambda file_name, file_content: handle_builder_add(
                file_name, file_content, builder.add_part_file
            ),
        )

    for folder in config.type_spec_types:
        find_and_handle_files(
            folder,
            name_regex=".*\\.(ts|py)\\.prepart",
            handler=lambda file_name, file_content: handle_builder_add(
                file_name, file_content, builder.add_prepart_file
            ),
        )

    def builder_prescan_file(file_name: str, file_content: str) -> None:
        name, _ = os.path.splitext(file_name)
        data = yaml.safe_load(file_content)
        # May be a placeholder file
        if data is None:
            data = {}
        try:
            builder.prescan(name.replace("/", "."), data)
        except Exception:
            print(f"Failure adding {file_name}")
            raise

    for folder in config.type_spec_types:
        find_and_handle_files(
            folder, name_regex=".*\\.yaml", handler=builder_prescan_file
        )

    if not builder.process():
        return None

    return builder
    return True

from __future__ import annotations

import dataclasses
import errno
import pathlib
import typing

import pysen
from pysen.component import LintComponentBase
from pysen.lint_command import LintCommandBase
from pysen.path import change_dir, resolve_path
from pysen.reporter import Reporter
from pysen.runner_options import PathContext
from pysen.setting import SettingBase, SettingFile, to_dash_case
from pysen.source import PythonFileFilter

from .preset import UNFIXABLE, preset_dict

CHECK_COMMAND = ["ruff", "check", "--show-source"]
FORMAT_COMMAND = ["ruff", "check", "--fix-only", "--show-fixes", "--exit-zero"]


class RuffCommand(LintCommandBase):
    def __init__(
        self: RuffCommand,
        paths: PathContext,
        source: pysen.Source,
        *,
        inplace_edit: bool,
    ) -> None:
        super().__init__(paths.base_dir, source)
        self._inplace_edit = inplace_edit
        self._setting_path = resolve_path(paths.settings_dir, "pyproject.toml")

    @property
    def name(self: RuffCommand) -> str:
        return "ruff"

    @property
    def has_side_effects(self: RuffCommand) -> bool:
        return self._inplace_edit

    def __call__(self: RuffCommand, reporter: Reporter) -> int:
        sources = self._get_sources(reporter, PythonFileFilter)
        msg = f"Checking {len(sources)} files"
        reporter.logger.info(msg)
        files = [str(s) for s in sources]
        command = FORMAT_COMMAND if self._inplace_edit else CHECK_COMMAND
        command = [*command, "--config", str(self._setting_path)]
        code = 0
        chunks = [files]
        with change_dir(self.base_dir):
            while len(chunks) > 0:
                chunk = chunks.pop()
                if len(chunk) == 0:
                    continue
                try:
                    returncode, _, _ = pysen.process_utils.run(
                        pysen.process_utils.add_python_executable(*command, *chunk),
                        reporter,
                    )
                    if returncode != 0:
                        code = returncode
                except OSError as e:
                    if len(chunk) >= 2 and e.errno == errno.E2BIG:
                        c = len(chunk) // 2
                        chunks.append(chunk[:c])
                        chunks.append(chunk[c:])
                    else:
                        raise

            return code


class RuffComponent(LintComponentBase):
    def __init__(
        self: RuffComponent,
        setting: RuffSetting,
        source: pysen.Source,
    ) -> None:
        super().__init__("ruff", source)
        self._setting = setting

    def export_settings(
        self: RuffComponent,
        paths: PathContext,
        files: typing.DefaultDict[str, SettingFile],
    ) -> None:
        files["pyproject.toml"].set_section(*self._setting.export())

    @property
    def targets(self: RuffComponent) -> typing.List[str]:
        return ["lint", "format"]

    def create_command(
        self: RuffComponent,
        target: str,
        paths: PathContext,
        options: pysen.RunOptions,
    ) -> pysen.CommandBase:
        return RuffCommand(paths, self.source, inplace_edit=(target == "format"))


class RuffPlugin(pysen.PluginBase):
    def load(
        self: RuffPlugin,
        file_path: pathlib.Path,
        config_data: pysen.PluginConfig,
        root: pysen.Config,
    ) -> typing.List[RuffComponent]:
        source = pysen.Source(includes=["."])
        setting = RuffSetting(**(config_data.config or {}))
        if root.lint:
            if root.lint.py_version:
                setting.target_version = root.lint.py_version.short_representation
            if root.lint.line_length:
                setting.line_length = root.lint.line_length
            if root.lint.isort_known_first_party:
                setting.isort = {"known-first-party": root.lint.isort_known_first_party}
            if root.lint.source:
                source = root.lint.source
        return [RuffComponent(setting, source=source)]


@dataclasses.dataclass(init=False)
class RuffSetting(SettingBase):
    select: typing.List[str]
    ignore: typing.List[str]
    unfixable: typing.List[str]
    target_version: typing.Optional[str] = None
    line_length: typing.Optional[int] = 88
    isort: typing.Optional[typing.Dict[str, typing.List[str]]] = None

    def __init__(self: RuffSetting, preset: str = "basic") -> None:
        self.select, self.ignore = preset_dict[preset]
        self.unfixable = UNFIXABLE

    def export(
        self: RuffSetting,
    ) -> typing.Tuple[typing.List[str], typing.Dict[str, typing.Any]]:
        return ["tool", "ruff"], self.asdict(omit_none=True, naming_rule=to_dash_case)

"""Module to generate a template for a new dashboard."""
import filecmp
import os
import shutil
from pathlib import Path


class ProjectAlreadyExistsError(Exception):
    """Exception raised when a project already exists."""


class _TemplateGenerator:
    PLACEHOLDER_SLUG = "@dashboard_slug@"
    DIRECTORY_NAME = "content"
    MAIN_FILE = "main%s.py"

    def __init__(self, dashboard_slug: str, tutorial: bool = False) -> None:
        self.__tutorial = tutorial
        self._dashboard_slug = dashboard_slug
        self.empty = True

    @property
    def _template_path(self) -> Path:
        return Path(f"{Path(__file__).parent.absolute()}/template")

    @property
    def _tutorial_path(self) -> Path:
        return Path(f"{Path(__file__).parent.absolute()}/tutorial_data")

    @property
    def _project_path(self) -> Path:
        return Path(Path(os.getcwd()) / f"{self._dashboard_slug}")

    def run(self) -> None:
        os.chdir(os.getcwd())
        self.__validate_project()
        self.__add_project()

    def __validate_project(self) -> None:
        """Validate current project."""
        if (
            not self.__tutorial
            and os.path.exists(self._dashboard_slug)
            or self.__tutorial
            and os.path.exists(self._project_path / "data")
        ):
            raise ProjectAlreadyExistsError()

    def __add_project(self):
        if not os.path.exists(self._project_path):
            self.__copy_paths()
            self.__update_dashboard_slug()

            self.__move_files()
            self.__create_dot_env()

        self.__copy_tutorial_files()

    def __copy_paths(self) -> None:
        shutil.copytree(
            self._template_path / self.DIRECTORY_NAME,
            Path(os.getcwd()) / self.DIRECTORY_NAME,
        )

    def __update_dashboard_slug(self) -> None:
        if self.empty:
            old_file = Path(self.DIRECTORY_NAME) / (self.MAIN_FILE % "_tmp")
            new_file = Path(self.DIRECTORY_NAME) / (self.MAIN_FILE % "")

            os.rename(new_file, old_file)

            with open(old_file, "r", encoding="UTF-8") as read:
                with open(new_file, "w", encoding="UTF-8") as write:
                    data = read.readlines()
                    for line in data:
                        if self.PLACEHOLDER_SLUG in line:
                            line = line.replace(
                                self.PLACEHOLDER_SLUG, self._dashboard_slug
                            )
                        write.write(line)

            os.remove(old_file)

    def __move_files(self) -> None:
        if not self.empty:
            os.mkdir(self._dashboard_slug)
            # We compare the files in the current directory with the files in the tmp
            # directory
            dir_diff = filecmp.dircmp(f"./{self.DIRECTORY_NAME}", "./tmp")
            # We move the common files to the tmp directory
            for filename in dir_diff.common:
                shutil.move(os.path.join("./tmp", filename), f"{self._dashboard_slug}")

            # We move the files that are only in the tmp directory to the parent
            # directory
            for filename in dir_diff.right_only:
                shutil.move(os.path.join("./tmp", filename), f"{self._dashboard_slug}")

            # We move the files that are only in the current directory to the parent
            # directory
            for filename in os.listdir(f"./{self.DIRECTORY_NAME}"):
                if filename not in dir_diff.common:
                    if filename in [".env.sample"] and os.path.exists(
                        f"{self._dashboard_slug}/.env"
                    ):
                        pass
                    else:
                        shutil.move(
                            os.path.join(f"./{self.DIRECTORY_NAME}", filename),
                            f"{self._dashboard_slug}",
                        )

        else:
            os.rename(self.DIRECTORY_NAME, self._dashboard_slug)

    def __create_dot_env(self) -> None:
        if not os.path.exists(f"{self._dashboard_slug}/.env"):
            os.rename(
                f"{self._dashboard_slug}/.env.sample", f"{self._dashboard_slug}/.env"
            )

    def __copy_tutorial_files(self):
        if self.__tutorial and not os.path.exists(self._project_path / "data"):
            shutil.copytree(
                self._tutorial_path,
                self._project_path / "data",
            )


def generate_template(dashboard_slug: str, tutorial: bool) -> None:
    """Interface to generate a template for a new dashboard.

    Args:
        dashboard_slug (str): Dashboard slug.
        tutorial (bool): If True, generate a template for a tutorial.
    """
    _TemplateGenerator(dashboard_slug, tutorial).run()


def remove_temporary_files():
    """Method that removes the temporary files created by the cookiecutter."""
    if os.path.isdir(main_folder := os.path.join(os.getcwd(), "content")):
        shutil.rmtree(main_folder)

    if os.path.isdir((tmp_folder := os.path.join(os.getcwd(), "tmp"))):
        shutil.rmtree(tmp_folder)

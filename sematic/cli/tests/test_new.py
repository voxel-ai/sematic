# Standard library
import random
import string
import os

# Third-party
from click.testing import CliRunner
import pytest

# Sematic
from sematic.cli.new import new
from sematic.cli.examples_utils import MIN_EXAMPLE_FILES, all_examples


@pytest.fixture
def project_name():
    return "".join(random.choice(string.ascii_lowercase) for i in range(7))


def test_new(project_name):
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(new, [project_name])

        assert result.output == "New project scaffold created at {}\n".format(
            os.path.join(os.getcwd(), project_name)
        )

        files = os.listdir(os.path.join(os.getcwd(), project_name))

    assert set(files) == {"main.py", "__init__.py", "requirements.txt", "pipeline.py"}


def test_new_already_exists(project_name):
    runner = CliRunner()

    with runner.isolated_filesystem():
        project_path = os.path.join(os.getcwd(), project_name)
        os.mkdir(project_path)

        result = runner.invoke(new, [project_name])

        assert result.output == "{} already exists.\n".format(project_path)


def test_from_unknown_example(project_name):
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(new, [project_name, "--from", "doesnotexist"])

        assert not os.path.exists(os.path.join(os.getcwd(), project_name))

        assert "Available examples are" in result.output


def test_from_example(project_name):
    runner = CliRunner()

    example_name = all_examples()[0]

    with runner.isolated_filesystem():
        result = runner.invoke(new, [project_name, "--from", example_name])

        project_path = os.path.join(os.getcwd(), project_name)
        assert os.path.exists(project_path)

        for file_name in MIN_EXAMPLE_FILES:
            assert os.path.exists(os.path.join(project_path, file_name))

        assert result.output == "New project scaffold created at {} from {}\n".format(
            os.path.join(os.getcwd(), project_name), example_name
        )

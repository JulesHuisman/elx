import json
import subprocess
import pytest
from elx.runner import Runner
from elx.singer import Singer
from elx.exceptions import DecodeException
from elx.json_temp_file import json_temp_file


def pipx_uninstall(executable: str) -> None:
    """
    Uninstall a package using pipx.

    Args:
        executable (str): The name of the package to uninstall.
    """
    subprocess.run(
        [
            "pipx",
            "uninstall",
            executable,
        ],
        check=False,
    )


def test_singer_can_discover_executable(singer: Singer):
    """
    Test that the singer executable can be discovered.
    """
    assert singer.executable == "tap-smoke-test"


def test_singer_can_install(singer: Singer):
    """
    Test that the singer executable is installed.
    """
    # Uninstall the singer executable if it is installed.
    pipx_uninstall(singer.executable)
    # Assert that the singer executable is not installed.
    assert not singer.is_installed
    # Install the singer executable.
    singer.install()
    # Assert that the singer executable is installed.
    assert singer.is_installed


def test_singer_can_run(singer: Singer):
    """
    Test that the singer executable can run.
    """
    # Uninstall the singer executable if it is installed.
    pipx_uninstall(singer.executable)
    # Run the executable and make sure it installs.
    with pytest.raises(DecodeException):
        singer.run(["--version"])


def test_singer_config_file(singer: Singer):
    """
    Test that the singer config file is created and deleted.
    """
    # Create the config file.
    with json_temp_file(singer.config) as config_path:
        # Assert that the config file exists.
        assert config_path.exists()
        # Open the config file and check that the content is the same as the config attribute.
        assert json.loads(config_path.read_text()) == singer.config
    # Assert that the config file no longer exists.
    assert not config_path.exists()


def test_singer_hash_key(singer: Singer):
    """
    Make sure the hash key is a valid md5 hash.
    """
    assert len(singer.hash_key) == 32


def test_singer_dynamic_config():
    """
    Make sure the Singer instance is able to handle dynamic config.
    """

    singer = Singer(
        executable="tap-smoke-test",
        spec="git+https://github.com/meltano/tap-smoke-test.git",
        config=lambda: {},
    )

    assert singer.config == {}


def test_singer_config_interpolation(runner: Runner):
    """
    Make sure the Singer instance is able to handle config interpolation.
    """

    singer = Singer(
        executable="tap-smoke-test",
        spec="git+https://github.com/meltano/tap-smoke-test.git",
        config={
            "target_schema": "{TAP_NAME}",
        },
    )

    # Attach the runner
    singer.runner = runner

    assert singer.config == {"target_schema": "tap_smoke_test"}

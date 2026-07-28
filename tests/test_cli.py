"""Tests for the CLI interface."""

from unittest.mock import patch

import pytest
from click.testing import CliRunner

from leetcode_profile_generator.cli import main


class TestCLI:
    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_version(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_missing_username(self, runner):
        result = runner.invoke(main, [])
        assert result.exit_code != 0

    def test_help(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "username" in result.output
        assert "theme" in result.output

    @patch("leetcode_profile_generator.cli.LeetCodeDataService")
    def test_invalid_theme(self, mock_service, runner):
        result = runner.invoke(main, ["--username", "test", "--theme", "nonexistent_theme"])
        assert result.exit_code != 0

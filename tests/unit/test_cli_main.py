"""
Unit tests for CLI main module.
"""

import pytest
from click.testing import CliRunner
from cli.main import cli


class TestCLIMain:
    """Test the main CLI interface."""

    def test_cli_help(self):
        """Test that CLI shows help message."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Prompt Learning CLI" in result.output
        assert "optimize" in result.output
        assert "image" in result.output

    def test_cli_version_option(self):
        """Test that CLI has version option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        # Version should be mentioned in help
        assert "--version" in result.output

    def test_cli_verbose_option(self):
        """Test that CLI has verbose option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "--verbose" in result.output or "-v" in result.output

    def test_optimize_command_exists(self):
        """Test that optimize command exists."""
        runner = CliRunner()
        result = runner.invoke(cli, ["optimize", "--help"])

        assert result.exit_code == 0
        assert "Optimize a prompt using natural language feedback" in result.output

    def test_image_command_exists(self):
        """Test that image command exists."""
        runner = CliRunner()
        result = runner.invoke(cli, ["image", "--help"])

        assert result.exit_code == 0
        assert "Test image generation prompts with nano banana" in result.output

    def test_invalid_command(self):
        """Test that invalid command shows error."""
        runner = CliRunner()
        result = runner.invoke(cli, ["nonexistent"])

        assert result.exit_code != 0
        assert "No such command" in result.output

    def test_optimize_missing_required_args(self):
        """Test optimize command fails without required arguments."""
        runner = CliRunner()
        result = runner.invoke(cli, ["optimize"])

        assert result.exit_code != 0
        assert "Missing option" in result.output or "Error" in result.output

    def test_image_missing_required_args(self):
        """Test image command fails without required arguments."""
        runner = CliRunner()
        result = runner.invoke(cli, ["image"])

        assert result.exit_code != 0
        assert "Missing option" in result.output or "Error" in result.output

    def test_global_verbose_flag(self):
        """Test global verbose flag is recognized."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--verbose", "optimize", "--help"])

        # Should still show help but with verbose enabled
        assert result.exit_code == 0

    def test_budget_option_in_optimize_help(self):
        """Test that budget option appears in optimize help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["optimize", "--help"])

        assert result.exit_code == 0
        assert "--budget" in result.output
        assert "$5" in result.output  # Default budget should be mentioned

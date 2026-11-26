"""Regression tests for the image CLI command."""

from click.testing import CliRunner

from cli.main import cli


def test_image_generation_failure(monkeypatch, mocker, tmp_path):
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    client = mocker.patch("providers.google_provider.genai.Client").return_value
    client.models.generate_content.side_effect = RuntimeError("Gemini unavailable")

    result = CliRunner().invoke(
        cli,
        ["image", "-p", "A red car", "-i", "2", "-o", str(tmp_path)],
    )

    assert result.exit_code == 1, result.output
    assert "Gemini unavailable" in result.output
    assert "Generated 2 images" not in result.output
    assert not list(tmp_path.iterdir())

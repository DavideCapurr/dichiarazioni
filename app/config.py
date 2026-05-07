from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    fic_access_token: str
    fic_company_id: int
    docx_template_path: str = "docx_templates/dichiarazione.docx"
    pdf_template_path: str | None = None

    @property
    def docx_template_abs_path(self) -> Path:
        """Resolve the Word template path relative to the project root."""
        path = Path(self.docx_template_path)
        if path.is_absolute():
            return path
        return Path(__file__).resolve().parent.parent / path

    @property
    def pdf_template_abs_path(self) -> Path:
        """Backward-compatible alias used by older tests/configuration."""
        return self.docx_template_abs_path


settings = Settings()

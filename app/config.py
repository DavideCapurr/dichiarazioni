from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    fic_access_token: str
    fic_company_id: int
    pdf_template_path: str = "pdf_templates/dichiarazione_conformita.pdf"

    @property
    def pdf_template_abs_path(self) -> Path:
        """Resolve the template path relative to the project root."""
        path = Path(self.pdf_template_path)
        if path.is_absolute():
            return path
        return Path(__file__).resolve().parent.parent / path


settings = Settings()

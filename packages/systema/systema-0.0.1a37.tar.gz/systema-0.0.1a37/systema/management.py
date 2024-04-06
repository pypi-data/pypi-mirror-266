import enum

from nanoid import generate
from platformdirs import user_config_path
from pydantic import AnyHttpUrl, DirectoryPath, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from systema.models.mode import Mode

BASE_DIR = user_config_path("systema", ensure_exists=True)
DB_FILENAME = ".db"
DOTENV_FILENAME = ".env"


class InstanceType(enum.StrEnum):
    SERVER = "server"
    CLIENT = "client"

    def other(self):
        if self == InstanceType.SERVER:
            return InstanceType.CLIENT
        if self == InstanceType.CLIENT:
            return InstanceType.SERVER
        raise NotImplementedError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="systema_",
        env_file=BASE_DIR / DOTENV_FILENAME,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    secret_key: str = Field(default_factory=generate)
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    base_path: DirectoryPath = Field(default=str(BASE_DIR))
    db_address: str = Field(default=f"sqlite:///{BASE_DIR}/{DB_FILENAME}")
    server_base_url: AnyHttpUrl = Field(default="http://0.0.0.0:8080/")
    offline_mode: bool = Field(default=False)
    instance_type: InstanceType = Field(default=InstanceType.SERVER)
    token: str = Field(default="")
    default_mode: Mode = Field(default=Mode.CHECKLIST)

    def to_dotenv(self, upper_case: bool = True, replace: bool = True):
        content = ""
        prefix = self.model_config.get("env_prefix", "")
        for key, value in self.model_dump(mode="json").items():
            key = prefix + key
            if upper_case:
                key = key.upper()
            content += f"{key}={value}\n"

        with open(self.base_path / DOTENV_FILENAME, mode="w") as file:
            if replace:
                file.flush()
            file.write(content)

    def check_dotenv(self):
        dotenv = self.base_path / DOTENV_FILENAME
        return dotenv.exists() and dotenv.is_file()

    def check_db(self):
        db = self.base_path / DB_FILENAME
        return db.exists() and db.is_file()

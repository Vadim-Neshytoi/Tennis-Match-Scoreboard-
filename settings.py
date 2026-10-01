import os
from dataclasses import dataclass
from pathlib import Path
from exceptions.validation_exceptions import ConfigurationError

@dataclass(frozen=True)
class Settings:
    """Хранит конфигурацию приложения, необходимую для его запуска."""

    db_url: str
    static_root: Path
    template_dir: Path
    host: str
    port: int

    @classmethod
    def load_from_env(cls) -> 'Settings':
        """Создаёт конфигурацию приложения на основе переменных окружения."""

        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ConfigurationError("Ошибка: Переменная окружения DATABASE_URL не задана !")

        base_dir = Path(__file__).resolve().parent

        raw_static = os.getenv("STATIC_ROOT")
        if raw_static:
            static_root = Path(raw_static)
            static_root = static_root.resolve() if static_root.is_absolute() else (base_dir / static_root).resolve()
        else:
            static_root = base_dir / "static"

        raw_template = os.getenv("TEMPLATE_DIR")
        if raw_template:
            template_dir = Path(raw_template)
            template_dir = template_dir.resolve() if template_dir.is_absolute() else (base_dir / template_dir).resolve()
        else:
            template_dir = base_dir / "templates"

        host = os.getenv("HOST", "0.0.0.0")
        raw_port = os.getenv("PORT", "8080")
        try:
            port = int(raw_port)
        except ValueError:
            raise ConfigurationError(f"Ошибка конфигурации: Порт должен быть числом, получено '{raw_port}'")
        if not (1 <= port <= 65535):
            raise ConfigurationError(f"Ошибка конфигурации: Порт {port} выходит за допустимый диапазон TCP портов (1-65535)")

        return cls(db_url=db_url,
                   static_root=static_root,
                   template_dir=template_dir,
                   host=host,
                   port=port)
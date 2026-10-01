from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape # noqa


class TemplateRenderer:
    """Рендерер HTML-шаблонов, преобразующий шаблон и данные контекста в HTML-контент."""

    def __init__(self, template_path: Path) -> None:
        self._env = Environment(loader=FileSystemLoader(str(template_path)), autoescape=select_autoescape(['html', 'xml']))
        # FileSystemLoader создаёт загрузчик шаблонов. Затем Environment(loader=...) создаёт окружение Jinja2

    def render(self, template_name: str, context: dict[str, object]) -> str:
        """Рендерит указанный шаблон, подставляя в него данные контекста"""

        template = self._env.get_template(template_name)
        return template.render(**context)































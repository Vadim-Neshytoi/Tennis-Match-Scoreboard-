from werkzeug.wrappers import Response, Request # noqa
from presentation.template_renderer import TemplateRenderer


class HomeController:
    """Контроллер, отвечающий за обработку HTTP-запросов к главной странице приложения."""

    def __init__(self, renderer: TemplateRenderer) -> None:
        self._renderer = renderer

    def show_home(self, _request: Request) -> Response:
        """Возвращает HTTP-ответ с главной страницей приложения."""

        html_content = self._renderer.render("index.html", {})

        return Response(response=html_content,
                        status=200,
                        mimetype="text/html")


















































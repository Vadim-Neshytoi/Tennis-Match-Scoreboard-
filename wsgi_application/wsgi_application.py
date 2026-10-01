from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from wsgiref.types import WSGIEnvironment, StartResponse
    from controllers.match_score_controller import MatchScoreController
    from controllers.matches_controller import MatchesController
    from controllers.new_match_controller import NewMatchController
    from controllers.home_controller import HomeController
    from wsgi_application.static_file_handler import StaticFileHandler

from werkzeug.wrappers import Response, Request # noqa
from typing import Callable, Iterable


type RouteHandler = Callable[[Request], Response]
STATIC_PREFIX = "/static/"


class WSGIApplication:
    """WSGI-приложение, отвечающее за маршрутизацию HTTP-запросов и передачу их соответствующим обработчикам."""

    def __init__(self, new_match_controller: NewMatchController, match_score_controller: MatchScoreController,
                 matches_controller: MatchesController, home_controller: HomeController,
                 file_handler: StaticFileHandler) -> None:
        self._new_match_controller = new_match_controller
        self._match_score_controller = match_score_controller
        self._matches_controller = matches_controller
        self._home_controller = home_controller
        self._file_handler = file_handler
        self._routes: dict[tuple[str, str], RouteHandler] = {}
        self._allowed_paths: set[str] = set()
        self._build_routes()

    def _build_routes(self) -> None:
        """Формирует таблицу маршрутов приложения."""

        self._routes = {
            ("/", "GET"): self._home_controller.show_home,
            ("/new-match", "GET"): self._new_match_controller.show_form, # bind methods
            ("/new-match", "POST"): self._new_match_controller.create_match,
            ("/match-score", "GET"): self._match_score_controller.show_score,
            ("/match-score", "POST"): self._match_score_controller.update_score,
            ("/matches", "GET"): self._matches_controller.show_finished_matches
        }
        self._allowed_paths = {k[0] for k in self._routes.keys()}

    def _match_route(self, path: str, method: str) -> tuple[RouteHandler | None, int | None]:
        """Определяет обработчик для указанного пути и HTTP-метода."""

        if path not in self._allowed_paths:
            return None, 404

        handler = self._routes.get((path, method))
        if handler is None:
            return None, 405

        return handler, None

    def __call__(self, environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
        """Обрабатывает входящий HTTP-запрос в соответствии с WSGI-протоколом."""

        request = Request(environ)
        if request.path.startswith("/static/"):
            if request.method not in ("GET", "HEAD"):
                response = Response("<h1>405 Method Not Allowed</h1>",
                                status=405,
                                content_type="text/html")
                response.headers["Allow"] = "GET, HEAD"
                return response(environ, start_response)
            relative_path = request.path[len(STATIC_PREFIX):]
            response = self._file_handler.handle(environ, relative_path)
        else:
            handler, status_code = self._match_route(request.path, request.method)

            if status_code == 404:
                response = Response("<h1>404 Not Found</h1>", status=404, content_type="text/html")
            elif status_code == 405:
                response = Response("<h1>405 Method Not Allowed</h1>", status=405, content_type="text/html")
            else:
                response = handler(request)

        return response(environ, start_response)














































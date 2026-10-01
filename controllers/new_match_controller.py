from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from application.application_services.match_creation_service import MatchCreationService
    from presentation.template_renderer import TemplateRenderer

from werkzeug.wrappers import Response, Request # noqa
from werkzeug.utils import redirect # noqa
from exceptions.validation_exceptions import InvalidPlayerNameError, DuplicateNamesAfterNormalizationError


class NewMatchController:
    """Контроллер, отвечающий за обработку HTTP-запросов страницы создания нового матча."""

    def __init__(self, app_service: MatchCreationService, renderer: TemplateRenderer) -> None:
        self._app_service = app_service
        self._renderer = renderer


    def create_match(self, request: Request) -> Response:
        """Обрабатывает HTTP-запрос на создание нового матча."""

        player_1_name = request.form.get("player_1_name")
        player_2_name = request.form.get("player_2_name")
        if player_1_name is None:
            view_data = self.make_view_data("player1", "Введите имя игрока", player_1_name, player_2_name)
            return self.make_response(view_data)
        if player_2_name is None:
            view_data = self.make_view_data("player2", "Введите имя игрока", player_1_name, player_2_name)
            return self.make_response(view_data)
        try:
            domain_match = self._app_service.create_match(player_1_name, player_2_name)
            redirect_url = f"/match-score?uuid={domain_match.uuid}"
            return redirect(redirect_url, code=303)
        except InvalidPlayerNameError as e:
            view_data = self.make_view_data(e.field_name, e.message, player_1_name, player_2_name)
            return self.make_response(view_data)
        except DuplicateNamesAfterNormalizationError as e:
            view_data = self.make_view_data(None, e.message, player_1_name, player_2_name)
            return self.make_response(view_data)


    def show_form(self, _request: Request) -> Response:
        """Возвращает HTTP-ответ с формой создания нового матча."""

        view_data = {
            "player_1_name": "",
            "player_2_name": "",
            "error": None,
        }
        html_content = self._renderer.render("new-match.html", view_data)
        return Response(response=html_content,
                        status=200,
                        mimetype="text/html")
    @staticmethod
    def make_view_data(field_name: str | None, message: str, player_1_name: str | None,
                       player_2_name: str | None) -> dict:
        """Формирует данные представления для рендеринга формы создания нового матча."""

        error_data = {
            "field": field_name,
            "message": message,
        }
        view_data = {
            "player_1_name": player_1_name,
            "player_2_name": player_2_name,
            "error": error_data,
        }
        return view_data

    def make_response(self, view_data: dict) -> Response:
        """Формирует HTTP-ответ с формой создания матча и ошибкой валидации."""

        html_content = self._renderer.render("new-match.html", view_data)
        return Response(response=html_content,
                        status=400,
                        mimetype="text/html")






















































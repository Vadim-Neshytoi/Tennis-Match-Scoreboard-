from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from application.application_services.match_query_service import MatchQueryService
    from application.application_services.match_score_application_service import MatchScoreApplicationService
    from mappers.match_view_mapper import MatchViewMapper
    from presentation.template_renderer import TemplateRenderer

from exceptions.validation_exceptions import MatchNotFoundError, PlayerNotInMatchError
import json
from werkzeug.wrappers import Response, Request # noqa
from werkzeug.utils import redirect # noqa


class MatchScoreController:
    """Контроллер, отвечающий за обработку HTTP-запросов страницы счёта матча."""

    def __init__(self, renderer: TemplateRenderer, match_query_service: MatchQueryService,
                 match_score_app_service: MatchScoreApplicationService, mapper: MatchViewMapper) -> None:
        self._renderer = renderer
        self._match_query_service = match_query_service
        self._match_score_app_service = match_score_app_service
        self._mapper = mapper

    def show_score(self, request: Request) -> Response:
        """Возвращает HTTP-ответ со страницей текущего счёта матча."""

        uuid = request.args.get("uuid")
        if not uuid or not uuid.strip():
            return Response(response=json.dumps({"error": "Параметр uuid обязателен для передачи и не может быть пустым"}),
                            status=400,
                            mimetype="application/json")
        cleaned_uuid = uuid.strip()
        try:
            domain_match = self._match_query_service.get_match_by_uuid(cleaned_uuid)
        except MatchNotFoundError as e:
            return Response(response=json.dumps({"error": str(e)}),
                            status=404,
                            mimetype="application/json")
        view_data = self._mapper.to_view_data(domain_match)
        html_content = self._renderer.render("match-score.html", view_data)
        return Response(response=html_content,
                        status=200,
                        mimetype="text/html")

    def update_score(self, request: Request) -> Response:
        """Обрабатывает HTTP-запрос на начисление очка выбранному игроку."""
        uuid = request.args.get("uuid")
        player_id = request.form.get("player_id")
        if not uuid or not uuid.strip():
            return Response(
                response=json.dumps({"error": "Параметр uuid обязателен для передачи и не может быть пустым"}),
                status=400,
                mimetype="application/json")
        if not player_id or not player_id.strip():
            return Response(
                response=json.dumps({"error": "Параметр player_id обязателен для передачи и не может быть пустым"}),
                status=400,
                mimetype="application/json")
        try:
            player_id = int(player_id)
        except ValueError:
            return Response(
                response=json.dumps({"error": "Параметр player_id должен быть исключительно числом"}),
                status=400,
                mimetype="application/json")
        cleaned_uuid = uuid.strip()
        try:
            domain_match = self._match_score_app_service.play_match(cleaned_uuid, player_id)
            redirect_url = f"/match-score?uuid={domain_match.uuid}"
            return redirect(redirect_url, code=303)
        except MatchNotFoundError as e:
            return Response(response=json.dumps({"error": str(e)}),
                            status=404,
                            mimetype="application/json")
        except PlayerNotInMatchError as e:
            return Response(response=json.dumps({"error": str(e)}),
                            status=404,
                            mimetype="application/json")





































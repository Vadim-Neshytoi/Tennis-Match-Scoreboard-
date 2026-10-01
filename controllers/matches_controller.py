from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from application.application_services.finished_matches_service import FinishedMatchesService
    from mappers.finished_match_view_mapper import FinishedMatchViewMapper
    from presentation.template_renderer import TemplateRenderer
    from validators.page_validator import PageValidator

import json
from exceptions.validation_exceptions import InvalidPageError, InvalidPlayerNameError, \
    DuplicateNamesAfterNormalizationError, PageNotFoundError
from werkzeug.wrappers import Response, Request # noqa


class MatchesController:
    """Контроллер, отвечающий за обработку HTTP-запросов со списком завершённых матчей."""

    def __init__(self, matches_service: FinishedMatchesService, matches_mapper: FinishedMatchViewMapper,
                 page_validator: PageValidator, renderer: TemplateRenderer) -> None:
        self._matches_service = matches_service
        self._matches_mapper = matches_mapper
        self._page_validator = page_validator
        self._renderer = renderer


    def show_finished_matches(self, request: Request) -> Response:
        """Возвращает HTTP-ответ со страницей завершённых матчей."""

        page = request.args.get('page')
        player_name = request.args.get('filter_by_player_name')
        if not page or not page.strip():
            page = "1"
        try:
            page = self._page_validator.validate_page(page)
        except InvalidPageError as e:
            return Response(response=json.dumps({"error": str(e)}),
                            status=400,
                            mimetype='application/json')
        if not player_name or not player_name.strip():
            player_name = None
        try:
            finished_matches_result = self._matches_service.get_finished_matches(page, player_name)
            view_data_matches = self._matches_mapper.to_view_data(finished_matches_result)
            html_content = self._renderer.render("matches.html", view_data_matches)
            return Response(response=html_content,
                            status=200,
                            mimetype='text/html')
        except (InvalidPlayerNameError, DuplicateNamesAfterNormalizationError, PageNotFoundError) as e:
            return Response(response=json.dumps({"error": str(e)}),
                            status=400,
                            mimetype='application/json')

































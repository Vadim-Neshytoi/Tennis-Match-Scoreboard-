import sys
from waitress import serve
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from application.application_services.finished_matches_service import FinishedMatchesService
from application.application_services.match_creation_service import MatchCreationService
from application.application_services.match_query_service import MatchQueryService
from application.application_services.match_score_application_service import MatchScoreApplicationService
from controllers.home_controller import HomeController
from controllers.match_score_controller import MatchScoreController
from controllers.matches_controller import MatchesController
from controllers.new_match_controller import NewMatchController
from exceptions.validation_exceptions import ConfigurationError
from mappers.finished_match_view_mapper import FinishedMatchViewMapper
from mappers.match_view_mapper import MatchViewMapper
from presentation.template_renderer import TemplateRenderer
from services.match_score_service import MatchScoreService
from settings import Settings
from unit_of_work.unit_of_work import UnitOfWork
from validators.page_validator import PageValidator
from validators.player_name_validator import PlayerNameValidator
from wsgi_application.static_file_handler import StaticFileHandler
from wsgi_application.wsgi_application import WSGIApplication


def create_application(db_url: str, static_root: Path, template_dir: Path) -> WSGIApplication:
    """Создаёт WSGI-приложение и его зависимости."""

    # ОБЪЕКТЫ ИНФРАСТРУКТУРЫ
    engine = create_engine(db_url, echo=False, pool_recycle=3600, pool_pre_ping=True)
    session_factory = sessionmaker(bind=engine)
    static_handler = StaticFileHandler(static_root=static_root)
    template_renderer = TemplateRenderer(template_path=template_dir)

    # ФАБРИКИ ЗАВИСИМОСТЕЙ
    uow_factory_callable = lambda: UnitOfWork(session_factory=session_factory)

    # СЕРВИСЫ (БИЗНЕС-ЛОГИКА)
    name_validator = PlayerNameValidator()
    match_score_service = MatchScoreService()
    match_creation_service = MatchCreationService(uow_factory=uow_factory_callable)
    match_query_service = MatchQueryService(uow_factory=uow_factory_callable)
    match_score_app_service = MatchScoreApplicationService(uow_factory=uow_factory_callable,
                                                           score_service=match_score_service)
    finished_matches_service = FinishedMatchesService(uow_factory=uow_factory_callable, name_validator=name_validator)

    # ИНТЕРФЕЙСНЫЙ СЛОЙ
    page_validator = PageValidator()
    matches_mapper = FinishedMatchViewMapper()
    match_view_mapper = MatchViewMapper(match_score_service)
    new_match_controller = NewMatchController(app_service=match_creation_service, renderer=template_renderer)
    match_score_controller = MatchScoreController(renderer=template_renderer, match_query_service=match_query_service,
                                                  match_score_app_service=match_score_app_service, mapper=match_view_mapper)
    matches_controller = MatchesController(matches_service=finished_matches_service, matches_mapper=matches_mapper,
                                           page_validator=page_validator, renderer=template_renderer)
    home_controller = HomeController(template_renderer)

    return WSGIApplication(new_match_controller=new_match_controller, match_score_controller=match_score_controller,
                           matches_controller=matches_controller, home_controller=home_controller, file_handler=static_handler)

def main() -> None:
    """Загружает настройки, создаёт приложение и запускает WSGI-сервер."""

    try:
        settings = Settings.load_from_env()
    except ConfigurationError as e:
        print(f"Критическая ошибка запуска: {e}", file=sys.stderr)
        sys.exit(1)

    wsgi_application = create_application(db_url=settings.db_url,
                                          static_root=settings.static_root,
                                          template_dir=settings.template_dir)
    serve(wsgi_application,
          host=settings.host,
          port=settings.port)

if __name__ == "__main__":
    main()














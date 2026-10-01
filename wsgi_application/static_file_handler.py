from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from wsgiref.types import WSGIEnvironment # noqa

import mimetypes
from pathlib import Path
from werkzeug.wrappers import Response # noqa
from werkzeug.wsgi import wrap_file # noqa


class StaticFileHandler:
    """Инфраструктурный компонент, отвечающий за выдачу статических файлов."""

    def __init__(self, static_root: str | Path) -> None:
        self._static_root = Path(static_root).resolve(strict=True) # .resolve(strict=True) делает две вещи.
        # Первая — превращает путь в абсолютный и нормализованный путь. static/../static/css/style.css
        # превратится в реальный путь к: .../static/css/style.css
        # Вторая — strict=True требует, чтобы путь существовал.

    def handle(self, environ: WSGIEnvironment, relative_path: str) -> Response:
        """Находит запрошенный статический файл и формирует HTTP-ответ с его содержимым."""

        try:
            requested_path = (self._static_root / relative_path.lstrip("/")).resolve(strict=True)
            is_valid_file = (requested_path.exists() and
                             requested_path.is_relative_to(self._static_root) and
                             requested_path.is_file())
            if not is_valid_file:
                return Response("<h1>404 File Not Found</h1>", status=404, mimetype="text/html")
        except (OSError, ValueError):
            return Response("<h1>404 File Not Found</h1>", status=404, mimetype="text/html")
        content_type, _ = mimetypes.guess_type(requested_path)
        content_type = content_type or "application/octet-stream"
        file_to_serve = requested_path.open("rb")
        file_iterator = wrap_file(environ, file_to_serve)
        return Response(file_iterator, status=200, content_type=content_type, direct_passthrough=True)


































import unittest
from pathlib import Path
from bs4 import BeautifulSoup # noqa
from presentation.template_renderer import TemplateRenderer


class TestMatchScoreTemplate(unittest.TestCase):

    def setUp(self) -> None:
        current_dir = Path(__file__).resolve().parent
        templates_path = current_dir.parent / 'templates'
        self.renderer = TemplateRenderer(templates_path)
        self.template_name = "match-score.html"

    def test_ongoing_match_ui(self) -> None:
        context = {
            "uuid": "abc-123",
            "player1": {"name": "Alex",
                        "id": 1,
                        "points": "0",
                        "games": 0,
                        "sets": 1},
            "player2": {"name": "Bob",
                        "id": 2,
                        "points": "0",
                        "games": 0,
                        "sets": 1},
            "winner": None
        }

        html_content = self.renderer.render(self.template_name, context)

        soup = BeautifulSoup(html_content, "html.parser")
        page_text = soup.get_text()

        input_p1 = soup.find("input", attrs={"type": "hidden", "name": "player_id", "value": 1})
        self.assertIsNotNone(input_p1, f"Скрытое поле для игрока с ID {1} должно быть на странице")
        form_p1 = input_p1.find_parent("form")
        self.assertIsNotNone(form_p1, "Input игрока 1 должен быть внутри формы")
        button_p1 = form_p1.find("button", class_="score-btn")
        self.assertIsNotNone(button_p1, "Кнопка 'Score' для игрока 1 должна быть внутри его формы")

        input_p2 = soup.find("input", attrs={"type": "hidden", "name": "player_id", "value": 2})
        self.assertIsNotNone(input_p2, f"Скрытое поле для игрока с ID {2} должно быть на странице")
        form_p2 = input_p2.find_parent("form")
        button_p2 = form_p2.find("button", class_="score-btn")
        self.assertIsNotNone(button_p2, "Кнопка 'Score' для игрока 2 должна быть внутри его формы")
        self.assertNotIn("Match Finished", page_text)
        self.assertIn("Current Match", page_text)

    def test_finished_match_ui(self) -> None:
        context = {
            "uuid": "abc-123",
            "player1": {"name": "Alex",
                        "id": 1,
                        "points": "0",
                        "games": 0,
                        "sets": 2},
            "player2": {"name": "Bob",
                        "id": 2,
                        "points": "0",
                        "games": 0,
                        "sets": 1},
            "winner": "Alex"
        }
        html_content = self.renderer.render(self.template_name, context)
        soup = BeautifulSoup(html_content, "html.parser")
        page_text = soup.get_text()
        input_p1 = soup.find("input", attrs={"type": "hidden", "name": "player_id", "value": 1})
        input_p2 = soup.find("input", attrs={"type": "hidden", "name": "player_id", "value": 2})
        self.assertIsNone(input_p1, "Скрытый input Игрока 1 должен исчезнуть после завершения матча")
        self.assertIsNone(input_p2, "Скрытый input Игрока 2 должен исчезнуть после завершения матча")
        any_score_button = soup.find("button", class_="score-btn")
        self.assertIsNone(any_score_button, "На табло не должно остаться кнопок 'Score'")

        self.assertIn("Match Finished", page_text)
        self.assertIn("Winner: Alex", page_text)
        self.assertNotIn("Current Match", page_text)
































import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from presentation.template_renderer import TemplateRenderer


class TestTemplateRenderer(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.temp_dir_path = Path(self.temp_dir.name)
        self.template_file = self.temp_dir_path / 'test.html'
        self.template_file.write_text('<h1>{{ title }}</h1>', encoding='utf-8')
        self.renderer = TemplateRenderer(template_path=self.temp_dir_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_template_render(self) -> None:
        html_result = self.renderer.render("test.html", {"title": "Alex"})

        self.assertEqual(html_result, "<h1>Alex</h1>")

    def test_template_render_autoescape(self) -> None:
        malicious_code = '<script>alert("x")</script>'
        html_result = self.renderer.render("test.html", {"title": malicious_code})

        self.assertNotIn(malicious_code, html_result)

        expected_escape_code = "<h1>&lt;script&gt;alert(&#34;x&#34;)&lt;/script&gt;</h1>"
        self.assertIn(html_result, expected_escape_code)

        self.assertEqual(html_result, expected_escape_code)





























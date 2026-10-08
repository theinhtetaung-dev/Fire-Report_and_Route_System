from urllib.parse import parse_qs, urlsplit

from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase

from .templatetags.pagination_ui import compact_pagination


class PaginationUITests(SimpleTestCase):
    def context(self, number, count=400):
        request = RequestFactory().get('/items/', {'q': 'fire & rescue', 'tag': ['a', 'b'], 'page': number})
        return {'request': request, 'page_obj': Paginator(range(count), 10).get_page(number)}

    def test_boundaries_and_elision(self):
        first = compact_pagination(self.context(1))
        self.assertFalse(first['previous_url'])
        self.assertTrue(first['next_url'])
        middle = compact_pagination(self.context(20))
        self.assertLess(len(middle['pages']), 16)
        self.assertEqual([item['number'] for item in middle['pages'] if item['current']], [20])
        self.assertFalse(compact_pagination(self.context(40))['next_url'])

    def test_filters_and_jump_form(self):
        data = compact_pagination(self.context(5), True)
        query = parse_qs(urlsplit(data['next_url']).query)
        self.assertEqual(query['q'], ['fire & rescue'])
        self.assertEqual(query['tag'], ['a', 'b'])
        self.assertEqual(query['page'], ['6'])
        self.assertNotIn('page', dict(data['query_pairs']))
        for name in ['pagination.html', 'emergency/pagination.html']:
            html = render_to_string(name, self.context(5))
            self.assertIn('aria-current="page"', html)
            self.assertIn('max="40"', html)
            self.assertIn('value="fire &amp; rescue"', html)

    def test_single_and_empty_pages(self):
        single = compact_pagination(self.context(1, 1))
        self.assertFalse(single['previous_url'])
        self.assertFalse(single['next_url'])
        self.assertEqual(len(single['pages']), 1)
        render_to_string('pagination.html', self.context(1, 0))

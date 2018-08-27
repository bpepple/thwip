from django.test import SimpleTestCase

from comics.utils.comicapi.utils import removearticles, listToString


class TestUtils(SimpleTestCase):

    def test_remove_articles(self):
        txt = 'The Champions & Inhumans'
        new_txt = removearticles(txt)
        self.assertEqual(new_txt, 'champions inhumans')

    def test_list_to_string(self):
        thislist = ["apple", "banana", "cherry"]
        expected_result = "apple, banana, cherry"

        list_string = listToString(thislist)
        self.assertEqual(list_string, expected_result)

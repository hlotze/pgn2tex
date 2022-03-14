"""Functions concerning pgn checks and docx generation"""
import unittest

from context import tex


class TestTex(unittest.TestCase):
    """Collection of tests for pgn module"""

    # Test 3
    def test_get_incremented_filename(self):
        """checks gene. of increm. filename if already exists"""
        # existing file 'docx_test_datatest_do_not_change' shall not be overwriten,
        # but a new file with incremented numbering shall be chosen as the new
        # file name; for the test: 'docx_test_data/test_do_not_change-1'
        self.assertTrue(tex.get_incremented_filename(
            'test/tex/test_do_not_change') ==
            'test/tex/test_do_not_change-1')

 

    # # Test 5
    # TODO
    # def test_gen_document_from_game(self):
    #     self.assertEqual(True, pgn.gen_document_from_game( params ))

    # # Test 6
    # TODO
    # def test_store_document(self):
    #     self.assertEqual(True, pgn.store_document( params ))


if __name__ == '__main__':
    unittest.main()

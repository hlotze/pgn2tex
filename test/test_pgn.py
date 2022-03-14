"""Functions concerning pgn; identify pgn 
files and get each file's pgn games"""
import unittest

from context import pgn


class TestPgn(unittest.TestCase):
    """Collection of tests for pgn module"""

    # # Test 1
    # def test_get_pgnfile_names_from_dir(self):
    #     """existance of at least one pgn-file in pgn-dir"""
    #     # there should be at least on file with extension
    #     # '.pgn' at directory 'PGN/TEST'
    #     self.assertTrue(len(pgn.get_pgnfile_names_from_dir( \
    #         pgn_dir='test/pgn', ext='.pgn')) > 0)

    # Test 2
    def test_get_games_from_pgnfile(self):
        """checks the pgn game retrieval from a pgn file"""
        # 'PGN/TEST/test_do_not_change.pgn' should contain 5 PGN games
        self.assertTrue(len(pgn.get_games_from_pgnfile(
            'test/pgn/test_do_not_change.pgn')) == 5)

 


if __name__ == '__main__':
    unittest.main()

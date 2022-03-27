# pylint: disable=import-error
# pylint: disable=protected-access
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
"""functions for pgn mgmt; identify pgn 
file and get each file's pgn games"""

import io
import os
import os.path
import re

import warnings

import chess
import chess.pgn
import numpy as np
import pandas as pd

import eco

warnings.simplefilter(action='ignore', category=FutureWarning)


def get_pgnfile_names_from_dir(pgn_dir='PGN/', ext='.pgn') -> list:
    """Return a python list with filenames
       from a given directory and given extension '.pgn' '.PGN'"""
    file_names_list = []
    for file in os.listdir(pgn_dir):
        if file.endswith(ext) or file.endswith(ext.upper()):
            if os.path.isfile(os.path.join(pgn_dir, file)):
                file_names_list.append(os.path.join(pgn_dir, file))
    return sorted(file_names_list)


def get_games_from_pgnfile(file_name: str) -> pd.DataFrame:
    """Return a DataFrame with all games of the file_name, incl. headers and pgn game notation."""
    with open(file_name, "r", encoding='utf-8') as pgn_file:
        games_df = pd.DataFrame()
        # iterate over all games of a file
        while True:
            try:
                game = chess.pgn.read_game(pgn_file)
                if game is None:
                    break
            except BaseException as err:
                print(f"Unexpected {err=}, {type(err)=}")
                print('at file:', file_name, 'with')
                print(game)
                continue
            
            game_dict = dict(game.headers)

            try:
                game_dict["pgn"] = game.board().variation_san(
                    game.mainline_moves())
            except BaseException as err:
                game_dict['pgn'] = ''
                # print(f"Unexpected {err=}, {type(err)=}")
                # print('at file:', file_name, 'with')
                # print(game)
                # continue

            game_dict['file'] = file_name

            # white & black names adjustments
            # "Carsen,Magnus" -->  "Carsen, Magnus"
            game_dict['White'] = ', '.join(game_dict['White'].split(',')).replace('  ',' ')
            game_dict['Black'] = ', '.join(game_dict['Black'].split(',')).replace('  ',' ')
            
            games_df = games_df.append(game_dict, ignore_index=True)
    # change in case of missing pgn,
    # all tags with value pd.NaN to ''
    # empty str
    for index, row_s in games_df.iterrows():
        for key, value in row_s.iteritems():
            if pd.isna(value):
                games_df.iloc[index][key] = ''
    #print(games_df)
    #print('\n')
    return games_df


def prep_game_data_from_pgn(pgn_str: str) -> pd.DataFrame:
    """Return for for each half-move information with 
    move fullmove-num+w/b, from-to squares, check square, lan_str"""
    # e.g.: 
    #   e2-e4  -> moveid: '1w', sq_from: 'e2', sq_to: 'e4', sq_check: '', lan_str: '1. e2-e4 ...'
    #   e7-e5  -> moveid: '1b', sq_from: 'e7', sq_to: 'e5', sq_check: '', lan_str: '1. ... e7-e5'
    #   Ng1-f3 -> moveid: '2w', sq_from: 'g1', sq_to: 'f3', sq_check: '', lan_str: '2. Ng1-f3 ...'
    #   Ng8-f6 -> moveid: '2b', sq_from: 'g8', sq_to: 'f6', sq_check: '', lan_str: '2. ... Ng8-f6'
    #   ...
    # start chess board
    board = chess.Board()
    game = chess.pgn.read_game(io.StringIO(pgn_str))
    
    if game == None:
        # return an empty pd.DataFrame()
        return pd.DataFrame({'moveid' : [],
                             'sq_from' : [],
                             'sq_to' : [],
                             'sq_check' : [],
                             'lan_str' : []})
    else:
        # prep for half moves
        half_moves_df = pd.DataFrame()
        for move in game.mainline_moves():
            # dict of half move infos
            move_dict = {}

            move = chess.Move.from_uci(move.uci())
            move_dict['moveid'] = str(int(board.fullmove_number))
            if chess.WHITE == board.turn:
                move_dict['moveid'] += 'w'
            else:
                move_dict['moveid'] += 'b'
            
            move_dict['lan'] = board.lan(move)

            # fromto for later markup
            move_dict['sq_from'] = move.uci()[:2]
            move_dict['sq_to'] = move.uci()[2:4]
            # site to move chess.WHITE or chess.BLACK

            if chess.WHITE == board.turn:
                move_dict['lan_str'] = \
                    str(int(board.fullmove_number)) + '. ' + \
                    board.lan(move) + ' ... '
            else:
                move_dict['lan_str'] = \
                    str(int(board.fullmove_number)) + '. ' + \
                    ' ... ' + board.lan(move)

            board.push(move)
            sq_check = ''
            if board.is_check():
                sq_check = chess.square_name(board.king(board.turn))
            move_dict['sq_check'] = sq_check

            half_moves_df = half_moves_df.append(move_dict, ignore_index=True)

        return half_moves_df


def main():
    """some test for the pgn.py"""
    ##################################################
    # this is for testing only
    # you need to create at your working directory
    # a directory PGN/, structured as the repo's PGN dir
    # or
    # change the code at
    #   pgn.main pgn_dir to whatever you need
    # the line here :
    ##################################################
    file_list = get_pgnfile_names_from_dir(pgn_dir='PGN/', ext='.pgn')
    print(file_list)

    for file_name in file_list:
        pgn_df = get_games_from_pgnfile(file_name)
        print('------------------------------')
        print(file_name)
        print(pgn_df.columns)
        print(pgn_df)


if __name__ == '__main__':
    main()

"""generates the tex files from given pgn by usage of module pgn2tex"""
import os.path
import sys

import pandas as pd

import eco
import pgn
import tex

def main():
    """Return the generated tex files"""
    pgn_dir = 'PGN'
    if not os.path.isdir(pgn_dir):
        print(f'directory \'{pgn_dir}\' does not exits, please create it.')
        sys.exit(1)
    file_names_list = pgn.get_pgnfile_names_from_dir(pgn_dir=pgn_dir)

    for fname in file_names_list:
        try:
            # check if file exists
            file_obj = open(fname, 'r')
            file_obj.close()

        except IOError:
            print("File not accessible: ", fname)
            continue
        finally:
            file_obj.close()

        # start to get the games out of one pgn file
        games_df = pgn.get_games_from_pgnfile(fname)

        for _, row in games_df.iterrows():
            one_game_dict = row.to_dict()

            if one_game_dict['pgn'] == '':
                pgn_available = False
            else:
                pgn_available = True

            eco_result_dict = {}
            if pgn_available == True:
                try:
                    if 'ECO' in one_game_dict.keys():
                        eco_result_dict = eco.new_get_eco_data_for(
                            eco=one_game_dict['ECO'],
                            pgn=one_game_dict['pgn'])
                    else:
                        eco_result_dict = eco.new_get_eco_data_for(
                            eco='',
                            pgn=one_game_dict['pgn'])
                except AttributeError as err:
                    eco_result_dict = {}
                    # print(f"\nUnexpected {err=}, {type(err)=}")
                    # print('no docx will be generated for game, as there is no pgn')
                    # print(one_game_dict)
                    # print('\n')
                    # continue

            chessboard_pgn_df = pgn.prep_game_data_from_pgn(one_game_dict['pgn'])

            tex_data = tex.gen_tex_data(one_game_dict,
                                        eco_result_dict,
                                        pgn_available,
                                        chessboard_pgn_df)

            # fn fix for lichess pgn files
            event = one_game_dict['Event'].replace(
                '/', '_').replace(':', '_').replace('.', '-')
            site = one_game_dict['Site'].replace(
                '/', '_').replace(':', '_').replace('.', '-')

            tex_fn = 'TEX/' + one_game_dict['Date'].replace('.', '-') + '_' + \
                event + '_' + \
                site + '_(' + \
                one_game_dict['White'] + ' - ' + \
                one_game_dict['Black'] + ')_(' + \
                one_game_dict['Result'].replace('/','_') + ')'

            if pgn_available == True:
                tex_fn += '_[' + one_game_dict['ECO'] + ']'

            tex_fn += '.tex'
            tex_fn = tex_fn.replace('?', 'x')

            ret_dict = tex.store_tex_document(tex_data, tex_fn)
            print('stored:', ret_dict['file_name'])



if __name__ == '__main__':
    main()
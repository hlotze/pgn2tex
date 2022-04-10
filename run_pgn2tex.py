"""generates the tex files from given pgn by usage of module pgn2tex"""
import os.path
import sys

import pandas as pd

import eco
import pgn
import tex
import config

def main():
    """Return the generated tex files"""
    pgn_dir = 'PGN'
    if not os.path.isdir(pgn_dir):
        print(f'directory \'{pgn_dir}\' does not exits, please create it.')
        sys.exit(1)
    file_names_list = pgn.get_pgnfile_names_from_dir(pgn_dir=pgn_dir)

    if config.analyse_games == True:
        pgn.process_pgns_analysis(file_names_list)

    if config.generate_games_tex == True:
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

            tex.mk_subdirs(fname, 'TEX/')

            # start to get the games out of one pgn file
            games_df = pgn.get_games_from_pgnfile(fname)

            games_df['Round4sort'] = games_df['Round'].apply(tex.prep_round4sort)
            games_df['Date'] = games_df['Date'].apply(tex.prep_date)
            games_df.sort_values(by=['Date', 'Site', 'Event', 'Round4sort'], inplace=True)

            print(str(len(games_df)) + ' games read at ' + fname)

            section_subfile_list = []
            for game_nr, game_s in games_df.iterrows():

                section_heading = ''
                if game_s['Site'] not in ['', ' ', '?', '*']:
                    section_heading = game_s['Site'] + ', '
                
                if game_s['Round'] not in ['', ' ', '?', '*']:
                    section_heading += game_s['Event'] + ', Round ' + \
                        game_s['Round'] + ' (' + \
                        game_s['Date'] + ')'
                else:
                    section_heading += game_s['Event'] + ' (' + \
                        game_s['Date'] + ')'

                if game_s['pgn'] == '':
                    pgn_available = False
                else:
                    pgn_available = True

                eco_result_dict = {}
                if pgn_available == True:
                    try:
                        if 'ECO' in game_s.keys():
                            eco_result_dict = eco.get_eco_data_for(
                                eco=game_s['ECO'],
                                pgn=game_s['pgn'])
                        else:
                            eco_result_dict = eco.get_eco_data_for(
                                eco='',
                                pgn=game_s['pgn'])
                    except AttributeError as err:
                        eco_result_dict = {}
                        # print(f"\nUnexpected {err=}, {type(err)=}")
                        # print('no docx will be generated for game, as there is no pgn')
                        # print(one_game_dict)
                        # print('\n')
                        # continue

                chessboard_pgn_df = pgn.prep_game_data_from_pgn(game_s['pgn'])

                tex_data = tex.gen_tex_data(game_s,
                                            eco_result_dict,
                                            pgn_available,
                                            chessboard_pgn_df)

                num_of_games = len(games_df)
                str_len_num_of_games = len(str(num_of_games))
                fn = str("0" * (str_len_num_of_games + 1)) + str(game_nr + 1)
                fn = fn[((str_len_num_of_games + 1) * -1):]
                tex_fn =  os.path.join(f'TEX/'+fname.split("/")[1].split(".")[0]+'/sections/', fn + '.tex')

                ret_dict = tex.store_tex_document(tex_data, tex_fn)
                print('stored:', ret_dict['file_name'])

                section_subfile_list.append({
                        'section' : section_heading,
                        'subfile' : tex_fn
                    })

            # generate the master tex file
            ret_dict = tex.generate_master_tex(fname, 'TEX/', section_subfile_list)
            print('stored:', ret_dict['file_name'], '\n')

            if len(games_df) > 250:
                print(fname + ' has ' + str(len(games_df)) + ' > 250')
                print('each tex-file will compile to a pdf-file, but')
                print('main.tex compilation may fail with standard')
                print('sizing in Tex live env using latexmk --g -pdf\n')
            else:
                print('goto [TEX/<subdir of the pgn-file_name>/sections/] and')
                print('e.g. start TEX to PDF processing in hatless mode by')
                print('latexmk --g -pdf (see latexmk --help)\n')


if __name__ == '__main__':
    main()
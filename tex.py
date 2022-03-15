# pylint: disable=import-error
# pylint: disable=protected-access
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
"""functions for tex generation"""

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
import pgn

warnings.simplefilter(action='ignore', category=FutureWarning)

def get_num_of_rows(length: int, cols: int) -> int:
    """Return the number of rows needed for a list with given length
    becomming an array with given cols"""
    if (length % cols) != 0:
        rows = length / cols + 1
    else:
        rows = length / cols
    return int(rows)


def gen_list(length: int, cols: int) -> list:
    """Return a list that fits to an array of given cols"""
    rows = get_num_of_rows(length, cols)
    arr = np.empty((rows, cols), dtype=str)
    for ze in range(arr.shape[0]):
        for sp in range(arr.shape[1]):
            arr[ze, sp] = ''
    return list(np.reshape(arr, cols*rows))



def gen_digram_table(white: str, 
                     black: str, 
                     cols : int, 
                     game_data_df: pd.DataFrame,
                     result: str) -> str:
    """Return the game's diagrams and lan into a table"""
    out = ''
    out += '\\begin{center}\n'
    
    if cols == 4:
        out += '\\begin{longtable}{C{40mm} C{40mm} C{40mm} C{40mm}}\n' + \
               '\\hline\n' + \
               white + ' & ' + black + ' & ' + \
               white + ' & ' + black + ' \\\\\n'

    if cols == 2:
        out += '\\begin{longtable}{C{40mm} C{40mm}}}\n' + \
               '\\hline\n' + \
               white + ' & ' + black + ' \\\\\n'
            
    out += '\\hline\n' + \
           '\\endhead\n\n'

    cb_arr = gen_list(len(game_data_df), cols)

    for cnt, row_s in game_data_df.iterrows():
        data = row_s.to_dict()
        cb_arr[cnt] = '% ' + data['lan_str'] + '\n' + \
               '\\xskakset{moveid=' + data['moveid'] + '}\n' + \
               '\\chessboard[setfen=\\xskakget{nextfen},\n' + \
               '             pgfstyle=border,\n' + \
               '             color=YellowGreen,\n' + \
               '             markfields={' + \
               data['sq_from'] + ',' + data['sq_to'] + '}'

        # arrows that shows the moves are to much at diagrams
        # cb_arr[cnt] += ',\n' + \
        #        '             pgfstyle=straightmove,\n' + \
        #        '             color=lightgray,\n' + \
        #        '             markmoves={' + \
        #        data['sq_from'] + '-' + data['sq_to'] + '}'

        if data['sq_check'] != '':
            cb_arr[cnt]  += ',\n' + \
               '             pgfstyle=circle,\n' + \
               '             color=BrickRed,\n' + \
               '             markfield={' + data['sq_check'] + '}]\n'
        else:
            cb_arr[cnt] += ']\n'

        if (cnt + 1) % cols > 0:
            if data['moveid'][-1] == 'w':
                cb_arr[cnt] += '\\newline\n' + \
                    data['moveid'][0:-1] + \
                    '.\\,\\xskakget{lan} ...\n'
            else:
                cb_arr[cnt] += '\\newline\n' + \
                    data['moveid'][0:-1] + \
                    '. ...\\,\\xskakget{lan}\n'
            if len(game_data_df) == cnt + 1:
                cb_arr[cnt] += '\\newline\n' + \
                    result + '\n'
            cb_arr[cnt] += '& \n'

        else:
            if data['moveid'][-1] == 'w':
                cb_arr[cnt] += '\\newline\n' + \
                    data['moveid'][0:-1] + \
                    '.\\,\\xskakget{lan} ...\n'
            else:
                cb_arr[cnt] += '\\newline\n' + \
                    data['moveid'][0:-1] + \
                    '. ...\\,\\xskakget{lan}\n'
            if len(game_data_df) == cnt + 1:
                cb_arr[cnt] += '\\newline\n' + \
                    result + '\n'
            cb_arr[cnt] += '\\\\[2mm] \n\n'

    # put arrays to out
    rows = int(len(cb_arr)/cols)
    cb_arr = np.reshape(cb_arr, (rows, cols))
    for ze in range(rows):
        for sp in range(cols):
            if cb_arr[ze, sp] != '':            
                out += cb_arr[ze, sp]
            else:
                if sp < cols -1:
                    out += '& \n'
                else:
                    out += '\\\\ \n'

    out += '\n\\end{longtable}\n' + \
           '\\end{center}\n'
    return out


def gen_tex_data(pgn_dict: dict, eco_dict: dict, pgn_available: bool, game_data_df: pd.DataFrame) -> str:
    """Return the tex data of a game; to be stored as a tex file"""
    out = ''
    out += '\\documentclass[9pt]{extarticle}\n' + \
        '\\usepackage[a4paper, total={180mm, 260mm}]{geometry}\n'
    if pgn_available == True:
        out += '\\usepackage{multicol}\n' + \
            '\n' + \
            '\\usepackage{longtable}\n' + \
            '\\setcounter{LTchunksize}{1000}\n' + \
            '\\usepackage{array}\n' + \
            '\\newcolumntype{C}[1]{>{\\centering\\let\\newline\\\\ \\arraybackslash\\hspace{0pt}}p{#1}}\n' + \
            '\n' + \
            '\\usepackage[dvipsnames]{xcolor}\n' + \
            '\\usepackage{xskak}\n' + \
            '\\usepackage{chessboard}\n' + \
            '\n'

    # fancyhdr for the header / footer 
    out += '\\usepackage{fancyhdr}\n' + \
        '\\usepackage[lastpage,user]{zref}\n' + \
        '\n' + \
        '\\pagestyle{fancy}\n' + \
        '\\fancyhf{}\n' + \
        '\\lhead{' + pgn_dict['Date'] + ': ' + pgn_dict['Event'] + \
        ' -- ' + pgn_dict['Site'] + '}\n' + \
        '\\rhead{' + pgn_dict['White'] + ' vs. ' + pgn_dict['Black'] + ' -- ' + \
        pgn_dict['Result']

    if pgn_available == True:
        out += ' -- ' + pgn_dict['ECO'] + '}\n'
    else:
        out += '}\n'

    out += '\\cfoot{\\thepage\\ of \\zpageref{LastPage}}\n\n'

    if pgn_available == True:
        # ifthen
        out += '\\usepackage{ifthen}\n' + \
            '\\newcommand{\\printmovercolor}[1]\n' + \
            '{\n' + \
            '    \\ifthenelse{\\equal{#1}{w}}\n' + \
            '     { % True case - w_hite\n' + \
            '         \\xskakgetgame{lastmovenr}.\\,\\xskakget{lan} ...\n' + \
            '     }\n' + \
            '     { % False case - b_lack\n' + \
            '         \\xskakgetgame{lastmovenr}. ... \\,\\xskakget{lan}\n' + \
            '     }\n' + \
            '}\n'

    if pgn_available == True:
        out += '\\setchessboard{tinyboard, showmover=false}\n\n'
    
    out += '\\begin{document}\n' + \
        '\\setlength{\\columnsep}{32pt}' + \
        '\n' + \
        '\\section*{' + pgn_dict['Date'] + ': ' + pgn_dict['Event'] + ' -- ' + \
        pgn_dict['Site'] + '}\n' + \
        '\n' + \
        '\\subsection*{' + pgn_dict['White'] + ' vs. ' + pgn_dict['Black'] + ' -- ' + \
        pgn_dict['Result']

    if pgn_available == True:
        out += ' -- ' + pgn_dict['ECO'] + '}\n'
    else:
        out += '}\n'

    out += "\\subsubsection*{Game's PGN}\n"

    # list pgn's tags, drop tags with no values given
    if pgn_available == True:
        out += '\\begin{multicols}{2}\n'

    out += '\\begin{flushleft}\n'

    for key in pgn_dict:
        if key not in ['pgn', 'file']:
            if pgn_dict[key] in ['','?']:
                continue
            if (key == 'ECO') and (pgn_available == False):
                continue
            else:
                out += '[' + key + '] "' + pgn_dict[key] + '"\n\n'
    out += '\\end{flushleft}\n' +\
        '\\parindent 0mm\n'

    if pgn_available == True:
        # display last half move's diagramm
        # get the last half-move of game_data_df
        game_data_dict = game_data_df.iloc[-1].to_dict()
        out += '\\begin{flushleft}\n' + \
            '\\newchessgame[id=overview]\n' + \
            '\\longmoves\n' + \
            '\\mainline{' + pgn_dict['pgn'] + '} \\quad ' + pgn_dict['Result'] + '\n' + \
            '\\end{flushleft}\n' + \
            '\\begin{center}\n' + \
            '\\begin{tabular}{C{80mm}}\n' + \
            '\\xskakset{moveid=\\xskakgetgame{lastmoveid}}\n' + \
            '\\chessboard[normalboard, setfen=\\xskakget{nextfen},\n' + \
            '             pgfstyle=border,\n' + \
            '             color=YellowGreen,\n' + \
            '             markfields={' + \
            game_data_dict['sq_from'] + ',' + game_data_dict['sq_to'] + '}'

        if game_data_dict['sq_check'] != '':
            out += ',\n' + \
            '             pgfstyle=circle,\n' + \
            '             color=BrickRed,\n' + \
            '             markfield={' + game_data_dict['sq_check'] + '}]\n'
        else:
            out += ']\n'
        
        if game_data_dict['moveid'][-1] == 'w':
            out += '\\newline\n' + \
                game_data_dict['moveid'][0:-1] + \
                '.\\,\\xskakget{lan} ... \\quad ' + pgn_dict['Result'] + '\n'
        else:
            out += '\\newline\n' + \
                game_data_dict['moveid'][0:-1] + \
                '. ...\\,\\xskakget{lan} \\quad ' + pgn_dict['Result'] + '\n'

        out += '\\end{tabular}\n' + \
            '\\end{center}\n' + \
            '\\columnbreak\n'

    # opening information
    # eco details from eco_dict
    if pgn_available == True:
        out += '\\subsubsection*{' + \
            eco_dict['eco'] + ' -- ' + eco_dict['title'] + '}\n' + \
            '\\begin{flushleft}\n' + \
            '\\newchessgame[id=eco]\n' + \
            '\\longmoves\n' + \
            '\\mainline{' + eco_dict['pgn'] + '}\n\n' + \
            '\\end{flushleft}\n' + \
            '\\begin{center}\n' + \
            '\\begin{tabular}{C{60mm}}\n' + \
            '\\chessboard[smallboard, setfen={' + eco_dict['fen'] + '},\n' + \
            '             pgfstyle=border,\n' + \
            '             color=YellowGreen,\n' + \
            '             markfields={' + \
            eco_dict['sq_from'] + ',' + eco_dict['sq_to'] + '}'

        if eco_dict['sq_check'] != '':
            out += ',\n' + \
            '             pgfstyle=circle,\n' + \
            '             color=BrickRed,\n' + \
            '             markfield={' + eco_dict['sq_check'] + '}]\n'
        else:
            out += ']\n'

        out += '\\newline\n' + \
            '\\xskakset{moveid=\\xskakgetgame{lastmoveid}}\n' + \
            '\\printmovercolor{\\xskakgetgame{lastplayer}}\n'

        out += '\\end{tabular}\n' + \
            '\\end{center}\n' + \
            '\\end{multicols}\n' + \
            '\n'

    # all games will start with 1. move
    # if this does not exist in pgn
    # the game was not played, and
    # no game diagrams can be shown
    if pgn_available == True:
        out += "\\subsubsection*{Game's diagrams}\n" + \
            '\\nopagebreak[4]\n' + \
            '\\newchessgame\n' + \
            '\\hidemoves{' + pgn_dict['pgn'] + '}\n' + \
            '\n'

        out += gen_digram_table(pgn_dict['White'], 
                                pgn_dict['Black'], 
                                4, # define num of cols
                                game_data_df,
                                pgn_dict['Result'])

    out += '\\end{document}\n'

    return out


def get_incremented_filename(filename: str) -> str:
    """Return the given filename if exists with an increment"""
    name, ext = os.path.splitext(filename)
    seq = 0
    # continue from existing sequence number if any
    rex = re.search(r"^(.*)-(\d+)$", name)
    if rex:
        name = rex[1]
        seq = int(rex[2])

    while os.path.exists(filename):
        seq += 1
        filename = f"{name}-{seq}{ext}"
    return filename


def store_tex_document(tex_doc: str, file_name: str) -> dict:
    """Return a dict{'done' : True,
    'file_name' : <file_name>} after
    Document is stored at 'file_name'"""
    file_name = get_incremented_filename(file_name)
    tex_file = open(file_name, "w")
    tex_file.write(tex_doc)
    tex_file.close()
    # check that file name ist stored
    return({'done': os.path.exists(file_name),
            'file_name': file_name})


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


if __name__ == '__main__':
    main()



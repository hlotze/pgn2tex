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
import config

warnings.simplefilter(action='ignore', category=FutureWarning)

def prep_round4sort(val: str) -> str:
    """Return a val that can be sorted easy"""
    return ('0000000' + val)[-7:]

def prep_date(val: str) -> str:
    """Return a date val w/o ?"""
    if '?' in val:
        return ''.join(val.replace('?','').split('.'))
    else:
        return val

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
    out += '\setlength\LTleft{0mm}\n'
    
    if cols == 4:
        out += '\\begin{longtable}{C{40mm} C{40mm} C{40mm} C{40mm}}\n' + \
            '\\hline\n' + \
            white + ' & ' + black + ' & ' + \
            white + ' & ' + black + ' \\\\ \n'
        out += '\\hline\n' + \
           '\\endhead\n\n'

    if cols == 2:
        out += '\\begin{longtable}{C{53mm} C{53mm} | R{51mm}}\n'

        out += '\\hline\n' + \
            '$\\square$ \\hspace{2mm} ' + white + ' & ' + \
            '$\\blacksquare$ \\hspace{2mm} ' +  black + \
            ' & Your Comment \\\\ \n'
        out += '\\hline\n' + \
            '\\endhead\n\n'

    if config.use_TeX_while_4_details == True:
        # games details by while at TeX file
        # but not sq_check will be marked
        out += '%init theGame start position\n' + \
            '\\xskakset{id=theGame, moveid=\\xskakgetgame{initmoveid}}\n' + \
            '\n' + \
            '%as long as we have a moveid\n' + \
            '\\whiledo{\\xskaktestmoveid{\\xskakget{movenr}}{\\xskakget{player}}}\n' + \
            '{%begin block\n' + \
            '	\\ifthenelse{\\equal{\\xskakget{player}}{w}}\n' + \
            '	{% w_hite player\n' + \
            '		\\chessboard[setfen=\\xskakget{nextfen},\n' + \
            '					pgfstyle=border,\n' + \
            '			        color=YellowGreen,\n' + \
            '			        markfields={\\xskakget{movefrom},\\xskakget{moveto}}]\n' + \
            '		\\newline\n' + \
            '		\\xskakget{movenr}.\\,\\xskakget{lan} ... &\n' + \
            '	}%\n' + \
            '	{% b_lack player\n' + \
            '		\\chessboard[setfen=\\xskakget{nextfen},\n' + \
            '					pgfstyle=border,\n' + \
            '			        color=YellowGreen,\n' + \
            '			        markfields={\\xskakget{movefrom},\\xskakget{moveto}}]\n' + \
            '		\\newline\n' + \
            '		\\xskakget{movenr}. ... \\,\\xskakget{lan} \\\\ \n' + \
            '	}%\n' + \
            '	\\xskakset{stepmoveid}\n' + \
            '}%end block\n'

    else:
        # games details writen by python script to 
        # TeX file
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

            # arrows that shows the moves 
            # are in most cases to much at 
            # the diagrams
            if config.move_arrows == True:
                cb_arr[cnt] += ',\n' + \
                    '             pgfstyle=straightmove,\n' + \
                    '             color=YellowGreen,\n' + \
                    '             markmoves={' + \
                    data['sq_from'] + '-' + data['sq_to'] + '}'

            # but a king in check will 
            # will mark
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
                cb_arr[cnt] += '\\\\ \n\n'

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

    out += '\n\\end{longtable}\n'

    return out


def list_2_2darr(my_list: list, cols: int) -> np.array:
    """Return from a list an 2d np.array with 3 columns"""
    my_temp_list = gen_list(len(my_list), 3)
    for _ in range(len(my_list)):
        my_temp_list[_] = my_list[_]
    return np.array(my_temp_list, dtype=str).reshape( (get_num_of_rows(len(my_temp_list), 3), 3) )


def gen_remaining_mainline(eco_str: str, pgn_str: str) -> str:
    """Return the remaining mainline, i.e. pgn_str - eco_str"""
    # generate from each move's list a 2d array of elements
    #   [['1.' 'e4'  'e5' ]
    #    ['2.' 'Bc4' 'Bc5']
    #    ['3.' 'c3'  ''   ]]

    eco_arr = list_2_2darr(eco_str.split(' '), 3)
    pgn_arr = list_2_2darr(pgn_str.split(' '), 3)

    if eco_arr[len(eco_arr)-1, 3-1] != '':
        pgn_arr = pgn_arr[len(eco_arr):,]
    else:
        pgn_arr[len(eco_arr)-1][0] += '..'
        pgn_arr[len(eco_arr)-1][1] = ''
        pgn_arr = pgn_arr[len(eco_arr)-1:]

    pgn_list = list(pgn_arr.flatten())
    new_pgn_str = ' '.join(pgn_list)

    return  new_pgn_str


def gen_tex_data(pgn_dict: dict, eco_dict: dict, pgn_available: bool, game_data_df: pd.DataFrame) -> str:
    """Return the tex data of a game; to be stored as a tex file"""
    out = '\\documentclass[../main.tex]{subfiles}\n' + \
        '\n' + \
        '\\begin{document}\n' + \
        '\n' + \
        '\\index{Players ! ' + pgn_dict['White'] + ' $\\square$' + '}\n' + \
        '\\index{Players ! ' + pgn_dict['Black'] + ' $\\blacksquare$' + '}\n' + \
        '\\subsection{' + pgn_dict['White'] + ' vs. ' + pgn_dict['Black'] + ' -- ' + \
        pgn_dict['Result']

    if pgn_available == True:
        out += ' -- ' + pgn_dict['ECO'] + '}\n'
    else:
        out += '}\n' + \
            '\n'

    out += '\\begin{multicols*}{2}\n' + \
        '\n'

    # opening information
    # eco details from eco_dict
    if pgn_available == True:
        out += "% Game's Opening ECO data\n" + \
            '\\index{Openings ! ' + eco_dict['eco'] + ' -- ' + eco_dict['title'] + '}\n' + \
            '\\subsubsection{' + \
            eco_dict['eco'] + ' -- ' + eco_dict['title'] + '}\n' + \
            '\\begin{flushleft}\n' + \
            '\\newchessgame[id=eco]\n' + \
            '\\longmoves\n' + \
            '\\mainline{' + eco_dict['pgn'] + '}\n' + \
            '\\begin{center}\n' + \
            '\\begin{tabular}{C{60mm}}\n' + \
            '\\chessboard[setfen={' + eco_dict['fen'] + '},\n' + \
            '             pgfstyle=border,\n' + \
            '             color=YellowGreen,\n' + \
            '             markfields={' + \
            eco_dict['sq_from'] + ',' + eco_dict['sq_to'] + '}'

        # arrows that shows the moves 
        # are in most cases to much at 
        # the diagrams
        if config.move_arrows == True:
            out += ',\n' + \
                '             pgfstyle=straightmove,\n' + \
                '             color=YellowGreen,\n' + \
                '             markmoves={' + \
                eco_dict['sq_from'] + '-' + eco_dict['sq_to'] + '}'

        if eco_dict['sq_check'] != '':
            out += ',\n' + \
            '             pgfstyle=circle,\n' + \
            '             color=BrickRed,\n' + \
            '             markfield={' + eco_dict['sq_check'] + '}]\n'
        else:
            out += ']\n'

        out += '\\newline\n' + \
            '\\xskakset{moveid=\\xskakgetgame{lastmoveid}}\n' + \
            '\\printmovercolor{\\xskakgetgame{lastplayer}}\n' + \
            '\\end{tabular}\n' + \
            '\\end{center}\n'

    # PGN TAGS
    out += '% PGN tags\n' + \
        '\\begin{tabular}{L{60mm} R{10mm}}\n' + \
        '\\multicolumn{2}{l}{\\textbf{'
    site_event = pgn_dict['Site'] + ', ' + pgn_dict['Event']
    if '?' in site_event:
        site_event = site_event.replace('?', '').replace(',', '')
    out += site_event.strip() + '}}\\\\ \n' + \
        '\multicolumn{2}{l}{' + \
        pgn_dict['Date']

    if pgn_dict['Round'] not in ['?', ' ', '']:
        out += ' Round ' + pgn_dict['Round']

    out += '}\\\\[3mm]\n'

    # White player
    out += '\\textbf{$\\square$ \\hspace{2mm} '
    if 'WhiteTitle' in pgn_dict.keys():
        out += ' ' + pgn_dict['WhiteTitle'] + ' '
    out += pgn_dict['White'] + '}' 
    if 'WhiteElo' in pgn_dict.keys():
        if pgn_dict['WhiteElo'] != '':
            out += ' (' + pgn_dict['WhiteElo'] + ') '
    if len(pgn_dict['Result']) > 1:
        out += ' & \\textbf{' + pgn_dict['Result'].split('-')[0] + '}\\\\ \n'
    else:
        out += ' & \\textbf{' + pgn_dict['Result'] + '}\\\\ \n'
    
    # Black player
    out += '\\textbf{$\\blacksquare$ \\hspace{2mm} '
    if 'BlackTitle' in pgn_dict.keys():
        out += ' ' + pgn_dict['BlackTitle'] + ' '
    out += pgn_dict['Black'] + '}' 
    if 'BlackElo' in pgn_dict.keys():
        if pgn_dict['BlackElo'] != '':
            out += ' (' + pgn_dict['BlackElo'] + ') '
    if len(pgn_dict['Result']) > 1:
        out += ' & \\textbf{' + pgn_dict['Result'].split('-')[1] + '}\\\\ \n'
    else:
        out += ' & \\textbf{' + pgn_dict['Result'] + '}\\\\ \n'

    out += '\\end{tabular}\n' + \
        '\n'

    if pgn_available == True:
        # display last half move's diagramm
        # get the last half-move of game_data_df
        game_data_dict = game_data_df.iloc[-1].to_dict()
        out += "% Game's final diagram and result\n" + \
            '\\newchessgame[id=overview]\n' + \
            '\\longmoves\n' + \
            '\\hidemoves{' + eco_dict['pgn'] + '}'

        remaining_mainline = gen_remaining_mainline(eco_dict['pgn'], pgn_dict['pgn'])
        out += '\\mainline{' + remaining_mainline + '}\n' + \
            '\n' + \
            '\\begin{center}\n' + \
            '\\begin{tabular}{C{60mm}}\n' + \
            '\\xskakset{moveid=\\xskakgetgame{lastmoveid}}\n' + \
            '\\chessboard[setfen=\\xskakget{nextfen},\n' + \
            '       pgfstyle=border,\n' + \
            '       color=YellowGreen,\n' + \
            '       markfields={' + \
            game_data_dict['sq_from'] + ',' + game_data_dict['sq_to'] + '}'

        # arrows that shows the moves 
        # are in most cases to much at 
        # the diagrams
        if config.move_arrows == True:
            out += ',\n' + \
                '             pgfstyle=straightmove,\n' + \
                '             color=YellowGreen,\n' + \
                '             markmoves={' + \
                game_data_dict['sq_from'] + '-' + game_data_dict['sq_to'] + '}'

        if game_data_dict['sq_check'] != '':
            out += ',\n' + \
            '       pgfstyle=circle,\n' + \
            '       color=BrickRed,\n' + \
            '       markfield={' + game_data_dict['sq_check'] + '}]\n'
        else:
            out += ']\n'
        
        if game_data_dict['moveid'][-1] == 'w':
            out += '\\newline\n' + \
                game_data_dict['moveid'][0:-1] + \
                '.\\,\\xskakget{lan} ...\n'
        else:
            out += '\\newline\n' + \
                game_data_dict['moveid'][0:-1] + \
                '. ...\\,\\xskakget{lan}\n'
        
        out += '\\newline\n' + \
            pgn_dict['Result']+ '\n'

        out += '\\end{tabular}\n' + \
            '\\end{center}\n' + \
            '\\end{flushleft}\n' + \
            '\\end{multicols*}\n' + \
            '\\newpage\n'
    else:
        out +='\\end{multicols*}\n' + \
            '\\newpage\n'
            
    if config.print_detailed_moves == True:
        if pgn_available == True:
            out += "% Game's diagrams\n" + \
                '\\newchessgame[id=theGame]\n' + \
                '\\hidemoves{' + pgn_dict['pgn'] + '}\n' + \
                '\n'

            out += gen_digram_table(pgn_dict['White'], 
                                    pgn_dict['Black'], 
                                    2, # define num of cols 2 or 4
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
    #file_name = get_incremented_filename(file_name)
    #print(file_name)
    tex_file = open(file_name, "w")
    tex_file.write(tex_doc)
    tex_file.close()
    # check that file name ist stored
    return({'done': os.path.exists(file_name),
            'file_name': file_name})


def mk_subdirs(pgn_fname: str, tex_path: str) -> dict:
    """Return subdirs at tex_path for a pgn-fname"""
    # pgn_fname <path>/<pgn>.pgn
    # -->
    #   TEX/<pgn>/
    #   TEX/<pgn>/images/
    #   TEX/<pgn>/sections/
    # not done here, but used later
    #   TEX/<pgn>/<pgn>.tex  <-- this is the master tex
    #                            which includes all 
    #                            tex files from the section dir
    pgn = pgn_fname.split("/")[1].split(".")[0]
    tex_work_dir = tex_path + pgn + '/'
    if not os.path.exists(tex_work_dir):
        os.makedirs(tex_work_dir, exist_ok=True)
        os.makedirs(tex_work_dir + 'images/', exist_ok=True)
        os.makedirs(tex_work_dir + 'sections/', exist_ok=True)

    return({'done': os.path.exists(tex_work_dir),
            'work_dir' : tex_work_dir,
            'images_dir' : tex_work_dir + 'images/',
            'sections_dir' : tex_work_dir + 'sections/'})


def init_preamble(pgn_fn : str) -> str:
    preamble = ''
    preamble += '% exarticle, if needed to allow 9pt font size\n' + \
        '\\documentclass[11pt]{article}\n' + \
        '\\usepackage{import}\n' + \
        '\n' + \
        '\\usepackage{geometry}\n' + \
        '\\geometry{\n' + \
        '   a4paper,\n' + \
        '   top=20mm,\n' + \
        '   bottom=20mm,\n' + \
        '   left=20mm,\n' + \
        '   right=20mm\n' + \
        '}\n' + \
        '\n' + \
        '\\newcommand*\\cleartoleftpage{%\n' + \
        '   \\clearpage\n' + \
        '   \\ifodd\\value{page}\\hbox{}\\newpage\\fi\n' + \
        '}\n' + \
        '\n' + \
        '% fonts\n' + \
        '\\usepackage{mathptmx}\n' + \
        '\\usepackage{amssymb}\n' + \
        '\n' + \
        '% hyperlinks at toc and PDF outline\n' + \
        '\\usepackage{hyperref}\n' + \
        '\\hypersetup{\n' + \
        '   colorlinks=true,\n' + \
        '   linkcolor=blue,\n' + \
        '   filecolor=magenta,\n' + \
        '   urlcolor=cyan}\n' + \
        '\\urlstyle{same}\n' + \
        '\n' + \
        '% do not like the counters before the titles\n' + \
        '\\setcounter{secnumdepth}{0}\n' + \
        '\n' + \
        '% two columns on frist page\n' + \
        '\\usepackage{multicol}\n' + \
        '\\setlength{\\columnsep}{32pt}\n' + \
        '\n' + \
        '% for table that can span more then one page\n' + \
        '\\usepackage{longtable}\n' + \
        '\\setcounter{LTchunksize}{1000}\n' + \
        '% table cell width used with centering\n' + \
        '\\usepackage{array}\n' + \
        '\\newcolumntype{L}[1]{>{\\raggedright\\let\\newline\\\\ \\arraybackslash\\hspace{0pt}}m{#1}}\n' + \
        '\\newcolumntype{C}[1]{>{\\centering\\let\\newline\\\\ \\arraybackslash\\hspace{0pt}}p{#1}}\n' + \
        '\\newcolumntype{R}[1]{>{\\raggedleft\\let\\newline\\\\ \\arraybackslash\\hspace{0pt}}m{#1}}\n' + \
        '\n' + \
        '% colors\n' + \
        '\\usepackage[dvipsnames]{xcolor}\n' + \
        '\n' + \
        '% chessboards\n' + \
        '\\usepackage{xskak}\n' + \
        '\\usepackage{chessboard}\n'
    # change from small board to tinyboard
    # if you need 4 cols of chessboard, i.e. 2 moves
    preamble += '\\setchessboard{smallboard, showmover=false}\n' + \
        '\\styleC % for tabular pgn notation\n' + \
        '\n' + \
        '% if you want to add any graphics manually\n' + \
        '\\usepackage{graphicx} % use graphics in png format\n' + \
        '\\graphicspath{ {images/} } % images dir is TEX/<pgn>/images/\n' + \
        '\n' + \
        '% last page number\n' + \
        '\\usepackage[lastpage,user]{zref}\n' + \
        '\n' + \
        '% header and footer\n' + \
        '\\usepackage{titleps}\n' + \
        '\\newpagestyle{mypage}{%\n' + \
        '   \\headrule\n' + \
        '   \\sethead{}{}{\\subsectiontitle}\n' + \
        '   \\footrule\n' + \
        '   \\setfoot{\\sectiontitle}{}{\\thepage\\ of \\zpageref{LastPage}}\n' + \
        '}\n' + \
        '\\settitlemarks{section,subsection,subsubsection}\n' + \
        '\\pagestyle{mypage}\n' + \
        '\n' + \
        '% index\n' + \
        '\\usepackage{makeidx}\n' + \
        '\\makeindex\n' + \
        '\\renewcommand{\indexname}{Index}\n' + \
        '\\usepackage[totoc]{idxlayout}\n' + \
        '\n' + \
        '% check if lastmove was w_hite or b_lack\n' + \
        '\\usepackage{ifthen}\n' + \
        '\\newcommand{\\printmovercolor}[1]\n' + \
        '{\n' + \
        '   \\ifthenelse{\\equal{#1}{w}}\n' + \
        '   { % True case - w_hite\n' + \
        '       \\xskakgetgame{lastmovenr}.\\,\\xskakget{lan} ...\n' + \
        '   }\n' + \
        '   { % False case - b_lack\n' + \
        '       \\xskakgetgame{lastmovenr}. ... \\,\\xskakget{lan}\n' + \
        '   }\n' + \
        '}\n' + \
        '\n' + \
        '\\usepackage{subfiles} % Best loaded last in the preamble\n' + \
        '\n' + \
        '% TODO: fill \\href{ ... } with the link where you got the pgn from\n' + \
        '%  e.g. \\href{https://theweekinchess.com/assets/files/pgn/tatamast22.pgn}\n' + \
        '%\\title{\\href{}{' + pgn_fn + '}}\n' + \
        '\\title{' + pgn_fn + '}\n' + \
        '\n' + \
        '% TODO: fill the \\date{ ... }\n' + \
        '%  e.g. \\date{18.01.2022}\n' + \
        '%\\date{}\n' + \
        '\n' + \
        '% TODO: fill \\href{ ... } with the home link of the site\n' + \
        '%  e.g. \\href{https://theweekinchess.com}\n' + \
        '%  and  the site name you want to emphazie \\emph{ ... }\n' + \
        '%  e.g. \\emph{The Week in Chess}\n' + \
        '%\\author{downloaded from \\href{}{\\emph{}}}' + \
        '\n' + \
        '\n' + \
        '\\begin{document}\n' + \
        '\n' + \
        '\\maketitle\n' + \
        '\n' + \
        '% TODO: fill \\includegraphics[width=15cm]{ ... }\n' + \
        '%       with png image name without extention .png\n' + \
        '%       the png image shall be stored at TEX/<png>/images/\n' + \
        '%  e.g. \\includegraphics[width=15cm]{participants}\n' + \
        '%\\begin{center}\n' + \
        '%\\includegraphics[width=15cm]{}\n' + \
        '%\\end{center}\n' + \
        '\\newpage\n' + \
        '\n' + \
        '\\tableofcontents\n' + \
        '\\newpage\n' + \
        '\n' + \
        '% put index page here\n' + \
        '\\printindex\n' + \
        '\n' + \
        '\\cleartoleftpage\n'
    return preamble    


def generate_master_tex(pgn_fname : str, tex_path : str, section_subfile_list : list) -> str:
    """Return the name of the tex master file and generates it for that pgn"""
    pgn = pgn_fname.split("/")[1].split(".")[0]
    tex_master_fn = tex_path + pgn + '/main' + '.tex'

    tex_doc = init_preamble(pgn + '.pgn')
 
    last_section_header = ''
    for _, item_dict in enumerate(section_subfile_list):
        if last_section_header != str(item_dict['section']):
            last_section_header = str(item_dict['section'])
            tex_doc += '\\section{' + item_dict['section'] + '}\n'

        name = item_dict['subfile'].split('/')[-1]
        subfile_name = 'sections/' + name.split('.')[0]
        if config.print_detailed_moves == True:
            tex_doc += '\\subfile{' + subfile_name + '}\n' + \
                '\n' + \
                '\\cleartoleftpage\n' + \
                '\n'
        else:
            tex_doc += '\\subfile{' + subfile_name + '}\n' + \
                '\n' + \
                '\\clearpage\n' + \
                '\n'

    tex_doc += '\\end{document}\n'
    return store_tex_document(tex_doc, tex_master_fn)





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



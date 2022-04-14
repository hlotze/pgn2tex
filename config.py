"""The central configuration for optional parameters"""

# uncomment the option you like to have

# Each halfmove's square-from and
# square-to are marked.
# If you additionally like to have an 
# arrow pointing from --> to
# set
#   move_arrows = True
#
# if
#   move_arrows = False
# no arrows are drawn, just the 
# square-from & -to are marked
#
move_arrows = False # default
#move_arrows = True


# if you like to have a diagram for each 
# halfmove set 
#   print_detailed_moves = True
#
# if
#   print_detailed_moves = False
# you will get the games overview
# one-pagers.
#
print_detailed_moves = True # default
#print_detailed_moves = False

# not implemented, so let it False
include_game_score = False # default
#include_game_score = True


# for future features
# not implemented
analyse_games = False
generate_games_tex = True

# generation of games details by TeX while
# no King in check (sq_check) marked
# use_TeX_while_4_details = True
use_TeX_while_4_details = False # default

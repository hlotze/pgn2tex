# pgn2tex

## What this site provides 
- a script `run_pgn2tex.py` that generates one TeX file from one chess PGN[^1] match, with a chessboard for each half move. 
  - the script processes all `*.pgn` files that it find at `PGN/` directory.
  - be aware, a PGN file can have thousends of games inside, and with this script each of its games will get a TeX file in `TEX/` directory
  - each game's TeX generation take about 1 minute (on my old machine.)
  - the script was not possible without [`python chess`](https://github.com/niklasf/python-chess) and for PDF generation: [`Tex Live`](https://www.tug.org/texlive/)

## My intention
... was to support myself learning chess by studying chess games offline form selected PGN printouts.
For online studies a good starting point learning chess is [lichess.org](https://lichess.org/) or others.
This approach provides a printout in B/W with more contrast as the colored PDFs at [lichess_puzzles_to_pdf](https://github.com/hlotze/lichess_puzzles_to_pdf).

## Steps
- check 
  - the PGN[^1] examples; see `PGN/`
  - the TeX examples; see `TEX/`
  - the PDF examples; see `PDF/`
  - requirements.txt for the venv

- run the Python script `run_pgn2tex.py`; its will generate TeX files only
- install a TeX Live with its editor's TeX Maker or TexWorks
- use your prefered TeX editor (Tex Maker, TeX Works, others) and generate the PDF file from a TeX file
- or use in batch mode aka 'hatless': `latexmk --gg -pdf` within you `TEX/` folder at the console

## Open item
- [ ] add ECO Opening diagram to each game's TeX
- [ ] collect all games' TeX file to one or multiple TeX file(s), so that one PDF will be generate
  - [ ] add a TOC
  - [ ] add bookmarks
- [ ] documentation, e.g. wiki 

## Contact
[@hlotze](https://github.com/hlotze)

## Footnotes
[^1]: PGN - see [Wikipedia Portable Game Notation](https://en.wikipedia.org/wiki/Portable_Game_Notation)

[^2]: ECO - see [Wikipedia: Encyclopaedia of Chess Openings](https://en.wikipedia.org/wiki/List_of_chess_openings) or a [Detailed opening library](https://www3.diism.unisi.it/~addabbo/ECO_aperture_scacchi.html)

[^3]: chess evaluation - see [chessprogramming.org/Evaluation](https://www.chessprogramming.org/Evaluation)

[^4]: SAN - see [Wikipedia: Algebraic_notation_(chess)](https://en.wikipedia.org/wiki/Algebraic_notation_(chess))

[^5]: TTF - see [Wikipedia: TrueType](https://en.wikipedia.org/wiki/TrueType)



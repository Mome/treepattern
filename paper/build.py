#! /usr/bin/python

from subprocess import call

# remove old files
call('rm *.out *.aux *.log *.pdf *.blg *.bbl *.dvi'.split())

# compile text file with references
call('pdflatex knoex_paper'.split())
call('bibtex knoex'.split())
call('pdflatex knoex_paper'.split())
call('pdflatex knoex_paper'.split())


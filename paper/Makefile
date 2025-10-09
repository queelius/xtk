# Makefile for LaTeX paper

# Main file
MAIN = main
PDF = $(MAIN).pdf

# LaTeX compiler
LATEX = pdflatex
BIBTEX = bibtex

# Flags
LATEX_FLAGS = -interaction=nonstopmode -halt-on-error

.PHONY: all clean distclean view

all: $(PDF)

$(PDF): $(MAIN).tex
	$(LATEX) $(LATEX_FLAGS) $(MAIN)
	# Run twice for references
	$(LATEX) $(LATEX_FLAGS) $(MAIN)

# Full build with bibliography
full: $(MAIN).tex
	$(LATEX) $(LATEX_FLAGS) $(MAIN)
	$(BIBTEX) $(MAIN)
	$(LATEX) $(LATEX_FLAGS) $(MAIN)
	$(LATEX) $(LATEX_FLAGS) $(MAIN)

# Clean auxiliary files
clean:
	rm -f *.aux *.log *.out *.toc *.bbl *.blg *.lof *.lot

# Clean everything including PDF
distclean: clean
	rm -f $(PDF)

# View PDF
view: $(PDF)
	xdg-open $(PDF) 2>/dev/null || open $(PDF) 2>/dev/null || echo "Please open $(PDF) manually"

# Continuous compilation (requires latexmk)
watch:
	latexmk -pdf -pvc $(MAIN)

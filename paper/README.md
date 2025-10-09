# XTK Technical Report

This directory contains the LaTeX source for the XTK technical report/paper.

## Building the Paper

### Requirements

- LaTeX distribution (TeX Live, MiKTeX, or MacTeX)
- `pdflatex`
- Standard LaTeX packages (see `main.tex` for full list)

### Compilation

Using Make:

```bash
make          # Quick build (no bibliography)
make full     # Full build with bibliography
make clean    # Remove auxiliary files
make distclean # Remove all generated files including PDF
make view     # Open the PDF after building
```

Using pdflatex directly:

```bash
pdflatex main.tex
pdflatex main.tex  # Run twice for references
```

For full build with bibliography:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

### Continuous Compilation

If you have `latexmk` installed:

```bash
make watch
```

This will automatically recompile when source files change.

## Document Structure

- `main.tex` - Main LaTeX file containing the complete technical report
- `Makefile` - Build automation
- `figures/` - Directory for figures (currently empty)

## Sections

The technical report includes:

1. **Introduction** - Motivation and contributions
2. **Background and Related Work** - Term rewriting systems and CAS
3. **Formal Foundations** - Pattern matching and rewrite semantics
4. **System Architecture** - Implementation details and algorithms
5. **Turing Completeness** - Proof of computational universality
6. **Tree Search for Theorem Proving** - Search algorithms and applications
7. **Practical Applications** - Examples in differentiation, algebra, etc.
8. **Performance Evaluation** - Benchmarks and comparisons
9. **Related Work** - Comparison with other systems
10. **Conclusion** - Summary and future work
11. **Appendices** - Rule reference and usage examples

## Output

The compilation produces `main.pdf`, a comprehensive technical report suitable for:

- Academic submission
- Technical documentation
- Research reference
- Educational material

## Customization

To customize the paper:

1. **Title/Author**: Edit the title page section in `main.tex`
2. **Add sections**: Insert new `\section{}` commands
3. **Add figures**: Place images in `figures/` and use `\includegraphics`
4. **Bibliography**: Add entries to the bibliography section
5. **Formatting**: Modify preamble for different styles

## License

The paper is part of the XTK project and follows the same MIT License.

## Contact

For questions or suggestions about the paper, please open an issue on the main XTK repository.

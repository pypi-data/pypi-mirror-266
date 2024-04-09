"""Module containing the Publication class."""
import jupytext
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor, TagRemovePreprocessor
from nbconvert.exporters import NotebookExporter
from traitlets.config import Config
import pathlib
import os
import sys
import inspect
import pypandoc
import docx2pdf  # Requires MS Word


class Publication:
    """For publishing Python scripts (.py) and notebooks (.ipynb).

    This class allows you to publish Python scripts (.py) and notebooks (.ipynb)
    to standalone output files of types pdf and docx or to output files of types
    md (Markdown) and tex (LaTeX) that can be included in another document.

    Attributes:
        title: The title of the publication
        author: The author of the publication
        subtitle: The subtitle of the publication

    Args:
        title: The title of the publication
        author: The author of the publication
        source_filename: The filename of the source file
    """

    def __init__(
        self,
        title: str | None = None,
        author: str | None = None,
        source_filename: str | None | pathlib.Path = None,
    ):
        if self.is_notebook():
            self.nowrite = True  # Don't want to write if executed from within an ipynb (infinite loop)
        else:
            self.nowrite = False
            self.title = title
            self.author = author
            if source_filename is None:  # Then use the calling file
                source_filename = pathlib.Path(
                    inspect.getframeinfo(sys._getframe(1)).filename
                )
            else:
                source_filename = pathlib.Path(source_filename)
            self.subtitle = (
                "Source Filename: "
                + f"{source_filename.parent.stem}/{source_filename.name}"
            )
            self.source_kind = source_filename.suffix
            self.source_filename = source_filename
            self.basename = self.basenamer(source_filename)
            self.jupytext = jupytext.read(source_filename)
            if self.source_kind == ".py":
                self.write(to="ipynb-tmp", tmp=True, clean=False)
                self.pypandoc = pypandoc.convert_file(
                    f".tmp_{self.basename}.ipynb", "rst"
                )
                self.cleanup()
            elif self.source_kind == ".ipynb":
                self.pypandoc = pypandoc.convert_file(source_filename, "rst")
            else:
                raise ValueError(f"Unknown source_kind={self.source_kind}")

    def basenamer(self, filename):
        """Return the basename of the filename (sans path and extension)."""
        return pathlib.Path(filename).stem

    def run(self):
        """Runs the temporary ipynb."""
        self.write(to="ipynb-tmp", tmp=True, clean=False)
        with open(f".tmp_{self.basename}.ipynb") as f:
            nb = nbformat.read(f, as_version=4)
        c = Config()
        c.TagRemovePreprocessor.remove_cell_tags = ("remove_cell",)
        c.TagRemovePreprocessor.remove_all_outputs_tags = ("remove_output",)
        # c.TagRemovePreprocessor.remove_input_tags = ("remove_input",) # I don't think this did anything ... handling in filter
        c.TagRemovePreprocessor.enabled = True
        c.ExecutePreprocessor.timeout = 600
        c.ExecutePreprocessor.kernel_name = "python3"
        c.NotebookExporter.preprocessors = [
            "nbconvert.preprocessors.ExecutePreprocessor",
            "nbconvert.preprocessors.TagRemovePreprocessor",
        ]
        exporter = NotebookExporter(config=c)
        exporter.register_preprocessor(ExecutePreprocessor(config=c), True)
        exporter.register_preprocessor(TagRemovePreprocessor(config=c), True)
        output = NotebookExporter(config=c).from_notebook_node(nb)
        with open(f".tmp_{self.basename}_executed.ipynb", "w") as f:
            f.write(output[0])

    def filter_absolute_path(self):
        """Returns the absolute path of the Lua filter filter.lua."""
        return pathlib.Path(__file__).parent / "filter.lua"

    def reference_doc_absolute_path(self):
        """Returns the absolute path of the Pandoc reference docx document pandoc_reference.docx."""
        return pathlib.Path(__file__).parent / "pandoc_reference.docx"

    def write(
        self, to: str, pdflatex: bool = True, tmp: bool = False, clean: bool = True
    ):
        """Writes the publication to a file of type ``to``.

        With two types of output file (argument ``to``), ``"docx"`` and ``"pdf"``, are standalone in the sense
        that they are complete documents ready for distribution. With the other two
        types of output file, ``"md"`` and ``"tex"``, a document intended to be included in
        another document is created.

        To use ``to="pdf"`` with ``pdflatex=True`` (default), you must have LaTeX installed.
        Any will do, but our favorite is `TeX Live <https://www.tug.org/texlive/>`_, which works on all
        major operating systems.
        To use ``to="pdf"`` with ``pdflatex=False``, you must have Microsoft Word installed.
        The use here of the ``docx2pdf`` package is buggy, so mileage may vary.

        Args:
            to: Format to write to (``"pdf"``, ``"docx"``, ``"md"``, ``"tex"``)
            pdflatex: Use LaTeX to create a pdf (default: ``True``)
            tmp: Create a temporary output files
                (may be deleted by ``clean``; default: ``False``)
            clean: Delete temporary output files (default: ``True``)

        Returns:
            ``None``

        Example:
            It can be used from within the file to be published, call it ``pub.py`` as follows:

            .. code-block:: python

                # %% This is a code cell
                x = 3

                # %% [markdown]
                # Here is a Markdown cell with some math: $x = 4$.

                # %% Another code cell
                x**2

                # %% [markdown]
                ## Here Is a Header
                # And some regular text.

                # %% Another code cell
                x**3 + 1

                # %% tags=["active-py"]
                # This cell will not appear in the output due to its tag
                import engcom
                pub = engcom.Publication(title="A Title", author="Your Name")
                pub.write(to="pdf")


            This publishes a pdf file ``pub.pdf`` that appears as follows:

            .. figure:: /figures/pub.png

                A published pdf file.

            Alternatively, the last cell could be left off and another file could be used to publish it:

            .. code-block:: python

                import engcom
                pub = engcom.Publication(
                    source_filename="pub.py", title="A Title", author="Your Name"
                )
                pub.write(to="pdf")

            Finally, a third alternative is to use the ``publish`` CLI from a terminal window:

            .. code-block:: bash

                publish pub.py pdf --title "A Title" --author "Your Name"

            In this example, we have used the ``"pdf"`` output for publishing.
            This requires installing LaTeX; see :ref:`Installing LaTeX for Publishing PDF Files`.
            Alternatively, ``"docx"`` could be used to create a Microsoft Word document.
            Finally, Markdown ``"md"`` and LaTeX ``"tex"`` can be used if you would like to include the published file in another document.
        """
        if self.nowrite:
            return None
        else:
            if tmp:
                tmp_str = ".tmp_"
            else:
                tmp_str = ""
            if to == "ipynb":
                jupytext.write(self.jupytext, f"{tmp_str}{self.basename}.ipynb")
            elif to == "ipynb-tmp":
                jupytext.write(self.jupytext, f"{tmp_str}{self.basename}.ipynb")
            elif to == "md" or to == "pdf" or to == "docx" or to == "tex":
                self.run()
                tmp_nb_executed = f".tmp_{self.basename}_executed.ipynb"
                filters = [str(self.filter_absolute_path())]
                if to == "md":
                    self.write(to="ipynb-tmp", tmp=True, clean=False)
                    output = pypandoc.convert_file(
                        tmp_nb_executed,
                        "md",
                        format="ipynb+raw_markdown",
                        outputfile=f"{tmp_str}{self.basename}.md",
                        filters=filters,
                    )
                    print(f"Markdown write output: {output}")
                elif to == "pdf":
                    if pdflatex:
                        extra_args = []
                        if self.title is not None:
                            extra_args.append(f"--metadata=title:{self.title}")
                            extra_args.append(f"--metadata=subtitle:{self.subtitle}")
                        if self.author is not None:
                            extra_args.append(f"--metadata=author:{self.author}")
                        self.write(to="ipynb-tmp", tmp=True, clean=False)
                        output = pypandoc.convert_file(
                            tmp_nb_executed,
                            "pdf",
                            outputfile=f"{tmp_str}{self.basename}.pdf",
                            extra_args=extra_args,
                        )
                        assert output == ""
                    else:
                        self.write(to="docx", tmp=True, clean=False)
                        docx2pdf.convert(
                            f".tmp_{self.basename}.docx",
                            f"{self.basename}.pdf",
                        )
                elif to == "docx":
                    self.write(to="ipynb-tmp", tmp=True, clean=False)
                    extra_args = [
                        "--reference-doc",
                        str(self.reference_doc_absolute_path()),
                    ]
                    if self.title is not None:
                        extra_args.append(f"--metadata=title:{self.title}")
                        extra_args.append(f"--metadata=subtitle:{self.subtitle}")
                    if self.author is not None:
                        extra_args.append(f"--metadata=author:{self.author}")
                    output = pypandoc.convert_file(
                        tmp_nb_executed,
                        "docx",
                        outputfile=f"{tmp_str}{self.basename}.docx",
                        extra_args=extra_args,
                        filters=filters,
                    )
                    assert output == ""
                elif to == "tex":
                    self.write(to="ipynb-tmp", tmp=True, clean=False)
                    self.write(to="md", tmp=True, clean=False)
                    output = pypandoc.convert_file(
                        f".tmp_{self.basename}.md",
                        "tex",
                        outputfile=f"{tmp_str}{self.basename}.tex",
                        filters=filters,
                    )
                    print(f"LaTeX write output: {output}")
                    # assert output == ""
            else:
                raise ValueError(f"Unkown target (to) format: {to}")
            if clean:
                self.cleanup()

    def cleanup(self):
        """Delete temporary files"""
        for filename in pathlib.Path(".").glob(".tmp*"):
            filename.unlink()

    def is_notebook(self) -> bool:
        """Returns True if executed from a Jupyter notebook."""
        try:
            shell = get_ipython().__class__.__name__
            if shell == "ZMQInteractiveShell":
                return True  # Jupyter notebook or qtconsole
            elif shell == "TerminalInteractiveShell":
                return True  # Terminal running IPython
            else:
                return False  # Other type (?)
        except NameError:
            return False  # Probably standard Python interpreter

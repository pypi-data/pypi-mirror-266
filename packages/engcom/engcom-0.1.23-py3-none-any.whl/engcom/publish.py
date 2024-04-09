import argparse
from engcom.publication import Publication

parser = argparse.ArgumentParser(
    description="Publish a Python script .py or Jupyter .ipynb file."
)
parser.add_argument(
    "source_filename", type=str, help="A Python script .py or Jupyter .ipynb file"
)
parser.add_argument("to", type=str, help="Destination type (md, pdf, or docx)")
parser.add_argument(
    "--title", type=str, required=False, default=None, help="Title of the document"
)
parser.add_argument(
    "--author", type=str, required=False, default=None, help="Author of the document"
)
parser.add_argument(
    "--pdflatex",
    type=str,
    required=False,
    default=True,
    help="Use pdflatex to build pdf (default: True)",
)
parser.add_argument("--noclean", default=False, action="store_true")
parser.add_argument("--clean", dest="noclean", action="store_false")


def main():
    args = parser.parse_args()
    pub = Publication(
        title=args.title,
        author=args.author,
        source_filename=args.source_filename,
    )
    pub.write(to=args.to, pdflatex=args.pdflatex, clean=(not args.noclean))
    return 0

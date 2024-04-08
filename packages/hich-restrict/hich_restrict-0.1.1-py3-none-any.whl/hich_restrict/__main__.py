import click
import time
import sys
from .restrict_manager import *

@click.command()
@click.option("--frag-file-format",
    type=click.Choice(RestrictManager.frag_file_format_options()),
    show_default=True,
    default=RestrictManager.frag_file_format_options()[0],
    help="Whether lines of fragments file are in .bed format (chrom start end) "
         "or 'chromlines' format (chrom end1 end2 end3...). Autodetect is "
         "based on first line of file, not filename.")
@click.option("--output-pairs",
    type=str,
    help="Filename for output .pairs file")
@click.argument("frag-file")
@click.argument("input-pairs")
def cli(frag_file_format, output_pairs, frag_file, input_pairs):
    """
    frag-file: a non-compressed plaintext file containing fragments. All
    fragments from a particular chromosome must be in one contiguous block,
    with ascending coordinates. All fragments in a chromosome must be
    adjacent (frag_n start = frag_n-1 end + 1).

    input-pairs: a text file containing pairs in .pairs format. Can be
    plaintext or compressed with gzip (.gz, .gzip) or lz4 (.lz4).
    """
    cmd = ' '.join(sys.argv)
    rm = RestrictManager()
    rm.setup(cmd, frag_file_format, output_pairs, frag_file, input_pairs)
    rm.tag()


if __name__ == "__main__":
    cli()
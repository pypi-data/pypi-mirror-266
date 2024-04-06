import click
import time
import sys
from .contacts import *
from .fragments import *

class RestrictManager:
    
    def setup(self, cmd, frag_file_format, output_pairs, frag_file, input_pairs):
        self.output_pairs = output_pairs
        reader = self.frag_reader(frag_file_format, frag_file)
        self.frag_finder = FragFinder(reader)
        self.contacts = PairsContactsReader(
            input_pairs, 
            extract_fields=["chrom1", "pos1", "chrom2", "pos2", "#"],
            add_before_columns = f"#hichheader: @PG ID:hich-restrict CL: {cmd} PN:hich-restrict\n",
            yield_line_with_item = True)

        self.frag_finder.load()
    
    def tag(self):
        file = None
        if self.output_pairs:
            file = open(self.output_pairs, 'w')

        for fields, line in self.contacts:
            if fields is not None:
                frag1 = self.frag_finder.find(fields['chrom1'], int(fields['pos1']))
                frag2 = self.frag_finder.find(fields['chrom2'], int(fields['pos2']))
                frag_tag = "\t".join([str(s) for s in frag1+frag2])
                new_line = f"{line.strip()}\t{frag_tag}\n"
            else:
                new_line = line
            if not file:
                click.echo(new_line.strip())
            else:
                file.write(new_line)
        
        if file:
            file.close()
        if self.output_pairs:
            autodetect_compress(self.output_pairs)
            

    def frag_reader(self, frag_file_format, frag_file):
        readers = self.frag_file_formats[frag_file_format]
        reader = None
        for reader_type in readers:
            try_reader = reader_type(frag_file)
            try:
                for r in try_reader:
                    break
            except:
                continue
            else:
                reader = try_reader
                break
        if reader is None:
            raise Exception("Failed to autodetect fragment file format.")
        reader.file.seek(0)
        return reader



    @classmethod
    def frag_file_format_options(cls):
        return list(cls.frag_file_formats)

    frag_file_formats = {
        "autodetect":[BedIntervalReader, ChromlinesIntervalReader],
        "bed":[BedIntervalReader],
        "chromlines":[ChromlinesIntervalReader]
    }

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
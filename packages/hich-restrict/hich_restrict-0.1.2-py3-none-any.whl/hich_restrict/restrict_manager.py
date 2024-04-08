import click
from .contacts import *
from .fragments import *

class RestrictManager:
    
    def setup(self, cmd, frag_file_format, output_pairs, frag_file, input_pairs):
        """
        Load restriction fragments into memory and set up i/o classes
        """
        # Manages reading various fragments file formats
        # (currently chromlines (i.e. chr1 end1 end2 end3...\n) and .bed)
        reader = self.frag_reader(frag_file_format, frag_file)

        # Manages interpolation search for restriction fragments
        # Here we use the reader to load the fragments into memory
        self.frag_finder = FragFinder(reader)
        self.frag_finder.load()

        # Manager for reading chromosome and position from contacts along
        # with the complete line to facilitate rewriting with fragtags added
        self.contacts = PairsContactsReader(
            input_pairs, 
            extract_fields=["chrom1", "pos1", "chrom2", "pos2", "#"],
            add_before_columns = f"#hichheader: @PG ID:hich-restrict CL: {cmd} PN:hich-restrict\n",
            yield_line_with_item = True)

        # Manager for writing contacts
        self.output_pairs = output_pairs

    def tag(self, buffer_size = 1000):
        """
        Rewrite file with contacts tagged with restriction fragments
        """
        # Check if we should write to stdout or to a file
        file = None
        compress = False
        if self.output_pairs:
            file = autodetect_open(self.output_pairs, 'wb')
            compress = detect_compression(self.output_pairs)
        
        buffer = []
        # Tag contacts and save
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
                buffer.append(new_line.strip())
                if len(buffer) >= buffer_size:
                    out = '\n'.join(buffer)
                    out = out.encode('utf-8') if compress else out
                    file.write(out)
                    buffer = []

        if file:
            out = '\n'.join(buffer)
            out = out.encode('utf-8') if compress else out
            file.write(out)
            file.close()
            

    def frag_reader(self, frag_file_format, frag_file):
        # Determine what reader to use based on user-specified parameters
        readers = self.frag_file_formats[frag_file_format]
        reader = None
        for reader_type in readers:
            # Autodetect fragment file format (if necessary) and validate
            # that file format is correct.
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

    # Obtain frag file format parameter options
    @classmethod
    def frag_file_format_options(cls):
        return list(cls.frag_file_formats.keys())

    # Associate frag-file-format parameters with readers
    frag_file_formats = {
        "autodetect":[BedIntervalReader, ChromlinesIntervalReader],
        "bed":[BedIntervalReader],
        "chromlines":[ChromlinesIntervalReader]
    }
from abc import ABC, abstractmethod
from pathlib import Path
import shutil
import tempfile
import os

def detect_compression_extension(filename, extensions):
    suffixes = set(Path(filename).suffixes)
    intersection = suffixes.intersection(extensions)
    if len(intersection) == 0:
        return ""
    elif len(intersection) > 1:
        raise Exception("Multiple compression format extensions from "
                       f"{extensions} found in {filename}.")    
    else:
        return list(intersection)[0]

def detect_compression(filename):
    extensions = {'gzip':['.gz', '.gzip'], 'lz4':['.lz4']}
    all_extensions = set([e for exts in extensions.values() for e in exts])
    extension = detect_compression_extension(filename, all_extensions)

    if not extension:
        return ''
    elif extension in extensions['gzip']:
        return 'gzip'
    elif extension in extensions['lz4']:
        return 'lz4'
    else:
        raise Exception("Error in autodetecting file format for "
                        f"{filename} with extension {extension} and "
                        f"autodetected extensions {extensions}.")

def autodetect_compress(filename):    
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_filename = temp_file.name
    shutil.move(filename, temp_filename)

    compression = detect_compression(filename)
    with open(temp_filename, 'rb') as f_in:
        with autodetect_open(filename, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(temp_filename)
    

def autodetect_open(filename, mode = 'rt'):
    def gzip_open(filename, mode):
        import gzip
        return gzip.open(filename, mode)
    def lz4_open(filename, mode):
        import lz4.frame
        return lz4.frame.open(filename, mode)

    compression = detect_compression(filename)
    if compression == 'gzip':
        return gzip_open(filename, mode)
    elif compression == 'lz4':
        return lz4_open(filename, mode)
    else:
        return open(filename, mode)



class ChromContactsReader (ABC):
    @abstractmethod
    def __init__(self, filename, field_order = None, extract_fields = None, yield_line = False):
        pass

    @abstractmethod
    def __iter__(self, fields):
        pass

    @abstractmethod
    def is_fields_line(self, line):
        pass

    @abstractmethod
    def extract_field_indexes(self, line):
        pass

class PairsContactsReader(ChromContactsReader):
    def __init__(self,
        filename,
        field_order = None,
        extract_fields = None,
        add_before_columns = None,
        yield_line_with_item = False
    ):
        self.filename = filename
        self.field_order = field_order
        self.extract = extract_fields
        self.add_before_columns = add_before_columns
        self.yield_line_with_item = yield_line_with_item

    def __iter__(self):
        with autodetect_open(self.filename) as file:
            for line in file:
                if self.extract is None:
                    yield line
                    continue
                if self.is_fields_line(line) and not self.field_order:
                    yield [None, self.add_before_columns]
                    self.field_order = self.extract_field_indexes(line)
                if line.startswith("#"):
                    for field in self.extract:
                        if line.startswith(field):
                            yield [None, line]
                            break
                else:
                    item = {}
                    fields = line.split()
                    for extract in self.extract:
                        if extract in self.field_order:
                            field = extract
                            idx = self.field_order[field]
                            item[field] = fields[idx]
                    if self.yield_line_with_item:
                        yield [item, line]
                    else:
                        yield [item, None]
    
    def is_fields_line(self, line):
        return line.startswith("#columns:")
    
    def extract_field_indexes(self, line):
        return {e[1]: e[0] for e in enumerate(line.split()[1:])}
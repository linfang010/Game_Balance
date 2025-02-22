import traceback
#from datetime import datetime
from pathlib import Path

from IO import FormattedFileIO


class KeyValueDB:
    _KeyValueDB_VERSION = 1

    def __init__(self, filepath = None):
        """
        Simple key/value database.

        each key/value pickled/unpickled separately,
        thus unpickling error will not corrupt whole db

          filepath(None) if None, DB will not be saved on disk
        """
        self._filepath = Path(filepath) if filepath is not None else None

        try:
            d = {}
            if self._filepath is not None:
                with FormattedFileIO(self._filepath, 'r+') as f:
                    ver, = f.read_fmt('I')
                    if ver == KeyValueDB._KeyValueDB_VERSION:
                        keys_len, = f.read_fmt('I')
                        for i in range(keys_len):
                            obj = f.read_pickled()
                            if obj is not None:
                                key, data = obj
                                d[key] = data
        except:
            d = {}
        self._data = d
        
    def clear(self):
        self._data = {}

    def get_value(self, key, default_value=None):
        """
        returns data by key or None
        """
        return self._data.get(key, default_value)

    def set_value(self, key, value):
        """
        set value by key
        """
        self._data[key] = value


    def save_data(self):
        if self._filepath is not None:
            try:
                with FormattedFileIO(self._filepath, 'w+') as f:
                    f.write_fmt('I', KeyValueDB._KeyValueDB_VERSION)

                    d = self._data
                    keys = list(d.keys())
                    f.write_fmt('I', len(keys))
                    for key in keys:
                        f.write_pickled( (key, d[key]) )

                    f.truncate()
            except:
                print(f'Unable to save the data. {traceback.format_exc()}')

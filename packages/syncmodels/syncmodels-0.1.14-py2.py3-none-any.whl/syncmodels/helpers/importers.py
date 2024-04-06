import os
import re
import pandas as pd


from agptools.files import fileiter


class ExcelImporter:
    def __init__(self):
        pass

    @classmethod
    def load(cls, path='.', file_pattern=None, col_pattern=None, value_pattern=None):

        file_pattern = file_pattern or [r"(?P<name>.*)(?P<ext>\.(csv|xls|xlsx))$"]

        if isinstance(path, str):
            path = [path]

        if isinstance(file_pattern, str):
            file_pattern = [file_pattern]
                

        col_pattern = col_pattern or [r"(?P<name>id)"]
        if isinstance(col_pattern, str):
            col_pattern = [col_pattern]
        
        value_pattern = value_pattern or []
        if isinstance(value_pattern, str):
            value_pattern = [value_pattern]        

            
        def find_idx(df):
            _col = df.columns
            for _, row in df.iterrows():
                for _idx, _pattern in enumerate(col_pattern):
                    name = _col[_idx]
                    if re.match(_pattern, name):
                        return _idx, name
                break
            return -1, ""
            
        def find_idx_from(data):            
            for key, value in data.items():
                _value = str(value).strip()
                for _pattern in value_pattern:
                    if re.match(_pattern, _value):
                        return key, value
            return -1, ""

        db = {}
        for top in path:
            top = os.path.abspath(top)
            for pat in file_pattern:
                for path, info in fileiter(top=top, regexp=pat, info="d", relative=True):
                    df = pd.read_excel(path)
                    # find the columns that match the index pattern
                    idx, idx_name = find_idx(df)

                    _col = df.columns
                    n = 0
                    for _idx, row in df.iterrows():
                        data = {k: row[k] for k in _col}
                        if not idx_name:
                            _key, uid = find_idx_from(data)
                        else:
                            uid = data[idx_name]
                            
                        if uid:
                            n += 1
                            db.setdefault(uid, {}).update(data)
                    print(f"Importing [{n:3}] beacons from {path}")
        return db

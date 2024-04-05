import io
from pathlib import Path

import pandas as pd


class DocumentLoader:

    def _read_txt(self, path: Path) -> str:
        with io.open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def bulk_load_documents(self, path: Path, ext='.txt') -> pd.DataFrame:
        ext = '.' + ext.lower().lstrip('.')
        documents = []
        documents_ids = []
        for file in path.glob(f'*{ext}'):
            with io.open(file, 'r', encoding='utf-8') as f:
                if ext == '.txt':
                    documents.append(self._read_txt(file))
                else:
                    raise ValueError(f'Unsupported file format: {ext}')
                documents_ids.append(file.stem)
        return pd.DataFrame({'id': documents_ids, 'text': documents})

    def load_document(self, path: Path, ext='.txt') -> str:
        if ext == '.txt':
            return self._read_txt(path)
        else:
            raise ValueError(f'Unsupported file format: {ext}')

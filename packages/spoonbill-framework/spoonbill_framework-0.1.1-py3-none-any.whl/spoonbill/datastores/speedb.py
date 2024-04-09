from spoonbill.datastores.rdict import RdictBase
from speedict import Rdict, Options, WriteBatch, SstFileWriter


class SpeedbStore(RdictBase):
    """
    A key-value store based on [speedict](https://github.com/speedb-io/speedb)
    """

    @classmethod
    def open(cls, path: str, strict=True, *args, **kwargs):
        store = Rdict(path, options=Options(**kwargs))
        return SpeedbStore(store, strict=strict)

    def _list_cf(self):
        return Rdict.list_cf(self._store.path())

    def _flush(self):
        path = self._store.path()
        self._store.close()
        Rdict.destroy(path)
        self._store = Rdict(path)
        self._size = 0

    def update(self, d: dict):
        wb = WriteBatch()
        count = 0
        for i, (key, value) in enumerate(d.items()):
            wb.put(key, value, self._store.get_column_family_handle('default'))
            if key not in self._store:
                count += 1
        self._store.write(wb)
        self._size += count
        return self

    def save(self, path: str, batch: int = 100000000, **kwargs):
        writer = SstFileWriter(options=Options(**kwargs))
        writer.open(path)
        for k, v in self.items():
            writer[k] = v
        writer.finish()
        return True

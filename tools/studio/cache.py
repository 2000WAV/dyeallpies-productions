"""The bake-once cache: a NumPy memmap of one record per source frame plus a JSON sidecar holding the
validity key (memory render-iteration-cache; the pull-up renderer's FFV1 variant is the same idea).

    c = BakeCache(path, key, shape=(n, H, W, 4), dtype=np.float16)
    if c.valid: layer = c.mm[i]                 # "bake valid, reading back"
    else:       c.mm[i] = ...; c.commit()      # the sidecar is written only after a complete bake

The key must be JSON-serialisable and is compared after a JSON round-trip: tuples become lists on
both sides (a tuple/list mismatch silently rebaked every composite for a day, 2026-09-12). `reason`
says which key entry changed when the cache is stale, so the log shows why a bake reran.
"""
import json, os
import numpy as np


class BakeCache:
    def __init__(self, path, key, shape, dtype=np.float16, resume_from=0):
        self.path = path; self.side = path + ".json"; self.shape = tuple(shape); self.dtype = dtype
        self.key = json.loads(json.dumps(key)); self.reason = None
        self.valid = self._check()
        if self.valid:
            self.mm = np.load(path, mmap_mode="r")
        else:
            mode = "r+" if (resume_from and os.path.exists(path)) else "w+"
            self.mm = np.lib.format.open_memmap(path, mode=mode, dtype=dtype, shape=self.shape)

    def _check(self):
        if not (os.path.exists(self.path) and os.path.exists(self.side)):
            self.reason = "no cache file"; return False
        try:
            old = json.load(open(self.side, encoding="utf-8"))
        except Exception as e:
            self.reason = f"sidecar unreadable ({e})"; return False
        if old == self.key:
            mm = np.load(self.path, mmap_mode="r")
            if mm.shape != self.shape or mm.dtype != np.dtype(self.dtype):
                self.reason = f"shape/dtype {mm.shape} {mm.dtype} != {self.shape} {np.dtype(self.dtype)}"; return False
            return True
        changed = [k for k in set(old) | set(self.key) if old.get(k) != self.key.get(k)]
        self.reason = "key changed: " + ", ".join(sorted(changed)); return False

    def commit(self):
        self.mm.flush()
        json.dump(self.key, open(self.side, "w", encoding="utf-8"))
        self.valid = True

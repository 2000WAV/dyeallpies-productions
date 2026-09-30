"""
Reps the athlete removes by hand ("that is someone else"), and a suggestion learnt from them.

Each rep carries a small signature from the analysis: torso_ratio (how big the tracked person is
next to the clip's usual size), x_rel (where across the frame) and facing. A removal is an example
of "not him"; the reps kept in a clip where he removed something are examples of "him". With at
least MIN_EACH examples of each, a nearest-neighbour on the standardised signature flags look-alikes
of the removed reps as suspect. Suspect reps are only flagged, never removed: he confirms.

Stored in one JSON file next to the viewer cache.
"""
import json, os
import numpy as np

MIN_EACH = 3
MATCH_S = 0.3        # a rep is the same rep if its time is within this many seconds


def rep_time(r):
    return r.get("t_transition", r.get("t_top"))


def signature(r):
    return [float(r.get("torso_ratio") or 1.0), float(r.get("x_rel") or 0.5), float(r.get("facing") or 1)]


class Feedback:
    def __init__(self, path):
        self.path = path
        self.data = dict(removed={}, samples={})
        if os.path.exists(path):
            with open(path) as f:
                self.data = json.load(f)

    def save(self):
        tmp = self.path + ".part"
        with open(tmp, "w") as f:
            json.dump(self.data, f, indent=1)
        os.replace(tmp, self.path)

    def is_removed(self, clip, t):
        return any(abs(t - x) <= MATCH_S for x in self.data["removed"].get(clip, []))

    def set(self, clip, t, removed, analysis):
        """Remove (or restore) the rep of `clip` at time `t`, and refresh this clip's examples."""
        ts = [x for x in self.data["removed"].get(clip, []) if abs(x - t) > MATCH_S]
        if removed:
            ts.append(float(t))
        self.data["removed"][clip] = ts
        reps = analysis.get("reps", [])
        self.data["samples"][clip] = [dict(t=rep_time(r), f=signature(r), label=int(self.is_removed(clip, rep_time(r))))
                                      for r in reps] if ts else []
        self.save()

    def _learner(self):
        s = [x for xs in self.data["samples"].values() for x in xs]
        X = np.array([x["f"] for x in s], float) if s else np.zeros((0, 3))
        y = np.array([x["label"] for x in s], int)
        if (y == 1).sum() < MIN_EACH or (y == 0).sum() < MIN_EACH:
            return None
        scale = X.std(axis=0) + 1e-3
        return X / scale, y, scale

    def annotate(self, clip, analysis):
        """Copy of the analysis with removed / suspect on every rep."""
        learnt = self._learner()
        reps = []
        for r in analysis.get("reps", []):
            r = dict(r, removed=self.is_removed(clip, rep_time(r)), suspect=False)
            if learnt is not None and not r["removed"]:
                X, y, scale = learnt
                dist = np.linalg.norm(X - np.array(signature(r)) / scale, axis=1)
                r["suspect"] = bool(y[int(np.argmin(dist))] == 1)
            reps.append(r)
        return dict(analysis, reps=reps)

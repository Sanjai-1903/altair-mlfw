"""
baselines.py - the "can you beat THIS?" ladder  (task A6, phase P2).
====================================================================
Standard library only (math).

Spec rule #1 (scientific honesty): before anyone is allowed to be
impressed by the SNN, we must show how well DUMB methods already do.
If a simple baseline matches the SNN, the honest answer is NO-GO.

The ladder, simplest first:
  B0  Majority     - always predict the most common class. The floor.
  B1  OneThreshold - flag when the biggest motor current is too high.
  B2  ZScore       - flag when ANY feature is far from normal (one-class).
  B3  Centroid     - nearest-centroid classifier on all features.

Each baseline has:
  fit(Xtr, ytr, Xval, yval, names)   -> learn from TRAIN, tune on VAL
  predict(X)                          -> list of 0/1 predictions
It never sees the test set during fit.
"""

import math


# ---------- small helpers (no numpy) ----------
def _col(X, j):
    return [row[j] for row in X]


def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def _std(xs):
    if not xs:
        return 0.0
    m = _mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


def _f1(y_true, y_pred):
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    return (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0


# ---------- B0: majority ----------
class MajorityBaseline:
    name = "B0_majority"

    def fit(self, Xtr, ytr, Xval, yval, names):
        ones = sum(ytr)
        self.guess = 1 if ones * 2 > len(ytr) else 0
        return self

    def predict(self, X):
        return [self.guess for _ in X]


# ---------- B1: one threshold on the biggest motor current ----------
class OneThresholdBaseline:
    name = "B1_one_threshold"

    def __init__(self):
        # which features are "currentX_max"
        self.cur_idx = []

    def _score(self, row):
        # score = the largest "current*_max" value in this window
        return max(row[j] for j in self.cur_idx)

    def fit(self, Xtr, ytr, Xval, yval, names):
        self.cur_idx = [j for j, nm in enumerate(names)
                        if nm.startswith("current") and nm.endswith("_max")]
        # baseline level from NOMINAL training windows only
        nominal_scores = [self._score(r) for r, y in zip(Xtr, ytr) if y == 0]
        self.mu = _mean(nominal_scores)
        self.sd = _std(nominal_scores)
        # try a few k values, keep the one with best F1 on VALIDATION
        best_k, best_f1 = 3.0, -1.0
        for k in [1, 1.5, 2, 2.5, 3, 4, 5, 6]:
            thr = self.mu + k * self.sd
            preds = [1 if self._score(r) > thr else 0 for r in Xval]
            score = _f1(yval, preds)
            if score > best_f1:
                best_f1, best_k = score, k
        self.threshold = self.mu + best_k * self.sd
        return self

    def predict(self, X):
        return [1 if self._score(r) > self.threshold else 0 for r in X]


# ---------- B2: one-class z-score over all features ----------
class ZScoreBaseline:
    name = "B2_zscore_oneclass"

    def fit(self, Xtr, ytr, Xval, yval, names):
        # mean/std per feature from NOMINAL training windows only
        nominal = [r for r, y in zip(Xtr, ytr) if y == 0]
        self.mu = [_mean(_col(nominal, j)) for j in range(len(names))]
        self.sd = [_std(_col(nominal, j)) or 1e-9 for j in range(len(names))]
        # pick threshold on VALIDATION by best F1
        best_thr, best_f1 = 3.0, -1.0
        for thr in [2, 3, 4, 5, 6, 8, 10]:
            preds = [1 if self._score(r) > thr else 0 for r in Xval]
            score = _f1(yval, preds)
            if score > best_f1:
                best_f1, best_thr = score, thr
        self.threshold = best_thr
        return self

    def _score(self, row):
        # the most "surprising" feature decides (max abs z-score)
        worst = 0.0
        for j, x in enumerate(row):
            z = abs(x - self.mu[j]) / self.sd[j]
            if z > worst:
                worst = z
        return worst

    def predict(self, X):
        return [1 if self._score(r) > self.threshold else 0 for r in X]


# ---------- B3: nearest-centroid classifier ----------
class CentroidBaseline:
    name = "B3_nearest_centroid"

    def fit(self, Xtr, ytr, Xval, yval, names):
        self.mu = [_mean(_col(Xtr, j)) for j in range(len(names))]
        self.sd = [_std(_col(Xtr, j)) or 1e-9 for j in range(len(names))]
        pos = [self._norm(r) for r, y in zip(Xtr, ytr) if y == 1]
        neg = [self._norm(r) for r, y in zip(Xtr, ytr) if y == 0]
        # if train had no off-nominal windows, B3 can't be built
        self.ok = len(pos) > 0 and len(neg) > 0
        if self.ok:
            self.c_pos = [_mean(_col(pos, j)) for j in range(len(names))]
            self.c_neg = [_mean(_col(neg, j)) for j in range(len(names))]
        return self

    def _norm(self, row):
        return [(row[j] - self.mu[j]) / self.sd[j] for j in range(len(row))]

    def _dist(self, a, b):
        return sum((a[j] - b[j]) ** 2 for j in range(len(a)))

    def predict(self, X):
        if not self.ok:
            return [0 for _ in X]
        preds = []
        for row in X:
            z = self._norm(row)
            preds.append(1 if self._dist(z, self.c_pos) < self._dist(z, self.c_neg) else 0)
        return preds


def all_baselines():
    """The ladder, in order."""
    return [MajorityBaseline(), OneThresholdBaseline(),
            ZScoreBaseline(), CentroidBaseline()]

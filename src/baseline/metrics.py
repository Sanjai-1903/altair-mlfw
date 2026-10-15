"""
metrics.py - score predictions honestly.
========================================
Standard library only.

For anomaly detection, plain "accuracy" lies: if only 1 window in 20 is
off-nominal, a model that says "all nominal" is 95% accurate and useless.
So we always report precision, recall, F1 AND the false-alarm rate -
because on a rover, crying wolf on normal terrain is a real cost.
"""


def confusion(y_true, y_pred):
    """Count tp, fp, fn, tn. Positive (1) = off-nominal."""
    tp = fp = fn = tn = 0
    for yt, yp in zip(y_true, y_pred):
        if yt == 1 and yp == 1:
            tp += 1
        elif yt == 0 and yp == 1:
            fp += 1
        elif yt == 1 and yp == 0:
            fn += 1
        else:
            tn += 1
    return tp, fp, fn, tn


def _safe_div(a, b):
    return a / b if b else 0.0


def evaluate(y_true, y_pred, window_seconds):
    """Return a dict of metrics."""
    tp, fp, fn, tn = confusion(y_true, y_pred)
    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    f1 = _safe_div(2 * precision * recall, precision + recall)
    accuracy = _safe_div(tp + tn, tp + fp + fn + tn)

    # fraction of NORMAL windows we wrongly flagged
    false_alarm_rate = _safe_div(fp, fp + tn)
    # how many false alarms per hour of normal driving
    nominal_hours = (fp + tn) * window_seconds / 3600.0
    false_alarms_per_hour = _safe_div(fp, nominal_hours)

    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
        "false_alarm_rate": false_alarm_rate,
        "false_alarms_per_hour": false_alarms_per_hour,
    }

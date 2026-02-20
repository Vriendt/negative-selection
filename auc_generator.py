from run_experiment import run, ChunkModifier, ChunkRemainderPolicy, Config
import numpy as np
from sklearn import metrics
from imblearn import metrics as imbmetrics
import matplotlib.pyplot as plt
from typing import Dict, Tuple, Any
from pathlib import Path

CORRECT_LABEL = 0
INCORRECT_LABEL = 1

def get_arrays(dict: Dict[str, Tuple[Any, float]], threshold: float):
        y_true = []
        y_pred = []
        for (label, value) in dict.values():
            if value <= threshold:
                y_pred.append(CORRECT_LABEL)
            else:
                y_pred.append(INCORRECT_LABEL)
            y_true.append(label)

        return (y_true, y_pred)

def get_arrays_for_auc_roc(dict: Dict[str, Tuple[Any, float]]):
    y_true = []
    y_pred = []
    for (label, value) in dict.values():
        y_pred.append(value)
        y_true.append(label)

    return (y_true, y_pred)

def calc(dict, n, r):
    sensitivity = [1.0]
    specificity = [1.0]

    previous = None
    for (_, item) in enumerate(dict.items()):
        score = item[1][1]

        if previous != score:
            y_true, y_pred = get_arrays(dict, score)
            sens_score = imbmetrics.sensitivity_score(y_true, y_pred, average='binary')
            spec_score = 1 - imbmetrics.specificity_score(y_true, y_pred, average='binary')
            
            sensitivity.append(sens_score)
            specificity.append(spec_score)


        previous = score
    score = metrics.roc_auc_score(*get_arrays_for_auc_roc(dict))
    print(n, r, score)

    # plt.title(f"Line Graph AUC={score}, n={n}, r={r}")
    # plt.xlabel("1-specificity")
    # plt.ylabel("sensitivity")

    sensitivity.append(0.0)
    specificity.append(0.0)
    # plt.plot(specificity, sensitivity, color="red")
    # plt.show()

# result = runAssignment1()


def testRun():
    conf = Config((9,12), (1,9), Path('./syscalls/snd-unm/snd-unm.train'), ChunkRemainderPolicy.PAD)
    files = [(Path('./syscalls/snd-unm/prepared/snd-unm.1.0.test'), 0), (Path('./syscalls/snd-unm/prepared/snd-unm.1.1.test'), 1)]
    return run(conf, files, ChunkModifier(), ChunkRemainderPolicy.PAD)

r = testRun()

for (n, r), v in r.items():
    calc(v, n, r)
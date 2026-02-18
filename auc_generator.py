from run_experiment import run4
import numpy as np
from sklearn import metrics
import matplotlib.pyplot as plt
print("You are in bitch")
y_true = np.array([1, 1, 2, 2])
y_score = np.array([0.1, 0.4, 0.35, 0.8])
fpr, tpr, thresholds = metrics.roc_curve(y_true, y_score, pos_label=2)
print(metrics.auc(fpr, tpr))



dict = run4()[(10,4)]
print(dict)

print("\n\n\n")

previous = None

sensitivity = np.array([])
specificity_inv = np.array([])

for (i, item) in enumerate(dict.items()):
    score = item[1][1]

    if previous != score:
        print(score)

    previous = score

#string: (language, float)



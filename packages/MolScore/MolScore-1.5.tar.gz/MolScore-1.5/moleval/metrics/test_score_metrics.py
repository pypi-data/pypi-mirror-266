import pandas as pd
import json
from moleval.metrics.score_metrics import ScoreMetrics

scores = pd.read_csv('/shared/morgan/SMILES-RNN/prompt/denovo/2023_11_20_SMILES-RNN_Aripiprazole_similarity/scores.csv')
print('Without budget')
metrics = ScoreMetrics(scores=scores, budget=None, n_jobs=4, target_smiles=["O=C1CCc2ccc(OCCCCN3CCN(c4cccc(Cl)c4Cl)CC3)cc2N1"])
results = metrics.get_metrics(endpoints=['single'], thresholds=[0.8], chemistry_filters_basic=True)
print(json.dumps(results, indent=2))

print('With budget of 1000 and no thresholds')
metrics = ScoreMetrics(scores=scores, budget=1000, n_jobs=4, target_smiles=["O=C1CCc2ccc(OCCCCN3CCN(c4cccc(Cl)c4Cl)CC3)cc2N1"])
results = metrics.get_metrics(endpoints=['single'], thresholds=[], chemistry_filters_basic=True)
print(json.dumps(results, indent=2))


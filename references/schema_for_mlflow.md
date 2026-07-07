# Schema

## Params storage
1. Model family
2. Feature set version (A vs B) but I haven't stored anything models trained on regime b, they are just in the notebook.
3. Random seed althrough i haven't stored this data too. I will have to look into it, If it is in the notebook cells.

## Metrics (Train/Val/Test)
1. ROC-AUC
2. PR-AUC
3. brier_score
4. precision
5. recall

## Model Specific Params
###  LR
1. max_iter
2. regularization

### XGB
1. Hyperparams searched by optuna

### MLP
1. no_hidden_layers, no of nodes
2. batch size
3. dropout(bool)
4. batchnorm(bool)
5. activation function

# artifacts
1. model
2. archi json
3. threshold json
3. optuna_study

btw i think there are two ways to store model specific params, on seperate fields or just as a artifact, same for metric. which would be better.

# tags
I don't know about this one.. what are actually tags and how exactly are they used?

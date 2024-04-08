import numpy as np
from sklearn.model_selection import cross_val_score, KFold
from sklearn.linear_model import LogisticRegression
from scipy.stats import ttest_ind, f_oneway

# Sample data and labels (replace with your own dataset)
X = np.random.rand(100, 10)
y = np.random.randint(0, 2, 100)

# Define your model (replace with your specific model)
model = LogisticRegression()

# Perform tenfold cross-validation
kf = KFold(n_splits=10, shuffle=True, random_state=42)

# Store performance metrics for each fold
metrics_list = []

for train_index, test_index in kf.split(X):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]

    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    metrics_list.append(accuracy)

# Perform t-test (example: comparing two models)
model1_metrics = metrics_list[:5]  # metrics from first model
model2_metrics = metrics_list[5:]  # metrics from second model

t_stat, p_value = ttest_ind(model1_metrics, model2_metrics)
print(f'T-test: t_stat={t_stat}, p_value={p_value}')

# Perform ANOVA (example: comparing multiple models)
f_stat, p_value_anova = f_oneway(metrics_list[:3], metrics_list[3:6], metrics_list[6:9])
print(f'ANOVA: f_stat={f_stat}, p_value={p_value_anova}')

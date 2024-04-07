### Based on the paper: J. S. Saravanan and A. Mahadevan, "AI based parameter estimation of ML model using Hybrid of Genetic Algorithm and Simulated Annealing," 2023 14th International Conference on Computing Communication and Networking Technologies (ICCCNT), Delhi, India, 2023, pp. 1-5, doi: 10.1109/ICCCNT56998.2023.10308077. 

# Hyperparameter Optimization with Genetic Algorithm and Simulated Annealing

This repository contains a Python package `jss_optimizer` for optimizing hyperparameters using genetic algorithm (GA) and simulated annealing (SA) hybrid optimization algorithm. 

## Installation

You can install the package using pip:

```bash
pip install jss_optimizer

```

# Usage Example

```python
from jss_optimizer.jss_optimizer import HyperparameterOptimizer
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Load dataset
df = pd.read_csv('dataset/heart_v2.csv')
X = df.drop('heart disease', axis=1)
y = df['heart disease']
X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.7, random_state=42)

# Define model and parameters
model = RandomForestClassifier
params = ['max_depth', 'min_samples_leaf', 'n_estimators']

# Create an instance of HyperparameterOptimizer
optimizer = HyperparameterOptimizer(model, params)

# Optimize hyperparameters using genetic algorithm
best_solution_genetic = optimizer.optimize(X_train, y_train, X_test, y_test)
print('Best solution found by genetic algorithm:', best_solution_genetic)

# NOTE
# Most of the time, genetic algorithm itself could give an optimal solution. But it could also get caught in a local optima. 
# To aviod such senarios, further optimization with simulated annealing is recommended.
# Use the solution that you see fit is optimal.  

# Perform simulated annealing 
best_solution_simulated_annealing = optimizer.simulate_annealing(best_solution_genetic, X_train, y_train, X_test, y_test)
print('Best solution found by GA-SA hybrid optimization algorithm:', best_solution_simulated_annealing)

```

## works are under progress to extend it to work with every data and model in any given senario

## Version Logs
### version: 0.1.1 - This will work only with Random Forest Classifier on any dataset. 
### version: 0.1.2 - Same as version: 0.1.1. Added improvements & support for train-test spitting with proper score metrics    
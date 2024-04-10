# Scorecard Generator

The Scorecard Generator is a Python library that facilitates the creation of scorecards from classification model predictions. Scorecards are commonly used in credit scoring and fraud or risk assessment to evaluate the creditworthiness or risk level of individuals.

## Features
- **Scorecard Creation**: Generate scorecards from the predictions of classification models.
- **Threshold Adjustment**: Automatically adjust scorecard thresholds to cover the desired score range.
- **Score Binning**: Assign scores to bins for easier interpretation and decision-making.
- **Decision Assignment**: Automatically assign decisions (e.g., Approve, Reject) based on user-defined thresholds.
- **Visual Highlighting**: Visualize the best threshold in the scorecard for easy identification.

## Function Map
<img src="https://github.com/knowusuboaky/scorecard_generator/blob/main/README_files/figure-markdown/mermaid-figure-1.png?raw=true" width="730" height="1615" alt="Optional Alt Text">

## Installation

You can install the Scorecard Generator via pip:

``` bash

pip install scorecard_generator==2.1.5
```

## Load Package
``` bash

from scorecard_generator import scorecard
```


## Usage

``` bash
# Import necessary modules
import numpy as np
import pandas as pd

from scorecard_generator import scorecard

# Load your trained classification model and data
# Replace these with your own data and model
classification_method = TrainedModel()
feature_names = FeatureNames
X_test = TestData
y_test = TestLabels

# Generate the scorecard
feature_score, total_score = scorecard(classification_method, feature_names, X_test, y_test, min_score=300, max_score=850)

# Print the feature scorecard
print(feature_score)

# Display the overall scorecard with highlighted best threshold
total_score
```
- In summary, the `scorecard` function takes a `trained classification model`, `feature names`, `test dataset features`, and `actual labels` as input. It then generates a scorecard based on the model's predictions and provides flexibility to adjust the `score range`. 

    - `classification_method`: This argument represents the trained classification model from which the scorecard will be generated. It should have a predict_proba method, which outputs the probabilities of each class.

    - `feature_names`: This argument is a list of feature names corresponding to the model's coefficients or feature importances. It helps in interpreting the scorecard by associating each feature with its importance or coefficient.

    - `X_test`: This argument represents the input features used by the model for prediction. It's typically a DataFrame or array-like structure containing the test dataset features.

    - `y_test`: This argument represents the actual labels from the test set. It's used to calculate ROC curve metrics and determine the best threshold for the scorecard.

    - `min_score`: This argument defines the minimum possible score on the scorecard. It defaults to 300 but can be adjusted based on the specific requirements of the application.

    - `max_score`: This argument defines the maximum possible score on the scorecard. It defaults to 850 but can be adjusted based on the specific requirements of the application.


## Supported Models

The Scorecard Generator supports the following classification models:

### Linear Models

1. **Logistic Regression** `(!!!HIGHLY RECOMMENDED!!!)`:
   - Logistic Regression is a linear model that is widely used for binary classification tasks.
   - It models the probability that a given input belongs to a certain class.
   - Logistic Regression assumes that the relationship between the features and the target variable is linear.
   - It's a popular choice for scorecards due to its simplicity and interpretability.

``` bash

from sklearn.linear_model import LogisticRegression

# Train Logistic Regression
logistic_model = LogisticRegression(max_iter=10000)
logistic_model.fit(X_train, y_train)
```

2. **Elastic Net Logistic Regression**:
   - Elastic Net Logistic Regression is a variant of logistic regression that combines L1 and L2 regularization.
   - It is useful when dealing with high-dimensional data and helps prevent overfitting.
   - Elastic Net regularization can handle multicollinearity among features by shrinking some coefficients and setting others to zero.

``` bash

from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

# Train Elastic Net Logistic Regression
elastic_net_model = make_pipeline(StandardScaler(), SGDClassifier(loss='log_loss', penalty='elasticnet', l1_ratio=0.5))
elastic_net_model.fit(X_train, y_train)
```

3. **Support Vector Classifier with Linear Kernel (Linear SVC)**:
   - Linear SVC is a linear classification model that finds the hyperplane that best separates the classes.
   - It works well for linearly separable data and is particularly effective in high-dimensional spaces.
   - Linear SVC aims to maximize the margin between the classes, making it robust to outliers.

``` bash

from sklearn.svm import SVC

# Train Support Vector Classifier with Linear Kernel
svc_model = SVC(kernel='linear', probability=True)
svc_model.fit(X_train, y_train)
```

### Non-Linear Models

1. **Random Forest Classifier**:
   - Random Forest is an ensemble learning method that constructs multiple decision trees during training.
   - It aggregates the predictions of individual trees to make more accurate predictions.
   - Random Forest is robust to overfitting and works well with both numerical and categorical features.

``` bash

from sklearn.ensemble import RandomForestClassifier

# Train Random Forest
random_forest_model = RandomForestClassifier(n_estimators=100)
random_forest_model.fit(X_train, y_train)
```

2. **Gradient Boosting Classifier**:
   - Gradient Boosting builds an ensemble of decision trees sequentially, where each tree corrects the errors of the previous one.
   - It combines multiple weak learners to create a strong learner, achieving high predictive accuracy.
   - Gradient Boosting is effective in handling complex relationships in the data but may be prone to overfitting.

``` bash

from sklearn.ensemble import GradientBoostingClassifier

# Train Gradient Boosting
gradient_boosting_model = GradientBoostingClassifier(n_estimators=100)
gradient_boosting_model.fit(X_train, y_train)
```

3. **Decision Tree Classifier**:
   - Decision Tree is a tree-like structure where each internal node represents a feature, each branch represents a decision based on that feature, and each leaf node represents a class label.
   - It partitions the feature space into regions, making it easy to interpret and visualize.
   - Decision Trees are prone to overfitting on noisy data but can capture complex decision boundaries.

``` bash

from sklearn.tree import DecisionTreeClassifier

# Train Decision Tree
decision_tree_model = DecisionTreeClassifier()
decision_tree_model.fit(X_train, y_train)
```
4. **Naive Bayes Classifier**:
   - Naive Bayes is a probabilistic classifier based on Bayes' theorem and the assumption of independence between features.
   - It's simple, fast, and works well with high-dimensional data.
   - Naive Bayes performs surprisingly well in many real-world scenarios, especially with text classification tasks.

``` bash

from sklearn.naive_bayes import GaussianNB

# Train Naive Bayes
naive_bayes_model = GaussianNB()
naive_bayes_model.fit(X_train, y_train)
```

## Ideal Uses of the Scorecard Generator
The Scorecard Generator is ideal for various applications, including but not limited to:

- **Credit Scoring:** Assessing creditworthiness and risk levels of individuals for loan approvals.
- **Insurance Risk Assessment:** Evaluating the risk of insurance claims and determining premiums.
- **Fraud Detection:** Identifying fraudulent activities in financial transactions.
- **Customer Churn Prediction:** Predicting the likelihood of customers leaving a service or subscription.
- **Medical Diagnosis:** Diagnosing medical conditions based on patient data.
- **Employee Attrition Prediction:** Predicting the likelihood of employees leaving a company.

The Scorecard Generator provides a flexible solution for creating scorecards tailored to various classification models, enabling informed decision-making in diverse applications.

## Contributing
Contributions to the Scorecard Generator are highly appreciated! Whether it's bug fixes, feature enhancements, or documentation improvements, your contributions can help make the library even more powerful and user-friendly for the community. Feel free to open issues, submit pull requests, or suggest new features on the project's GitHub repository.

## Documentation & Examples
For documentation and usage examples, visit the GitHub repository: https://github.com/knowusuboaky/scorecard_generator

**Author**: Kwadwo Daddy Nyame Owusu - Boakye\
**Email**: kwadwo.owusuboakye@outlook.com\
**License**: MIT

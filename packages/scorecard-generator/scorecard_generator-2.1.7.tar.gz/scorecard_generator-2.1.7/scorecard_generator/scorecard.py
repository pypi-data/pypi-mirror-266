import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC



# Define the function to highlight the best threshold
def highlight_best_threshold(df, best_threshold):
    """
    Highlights the entire row with the best threshold in the DataFrame.
    
    Parameters:
    - df: DataFrame containing the thresholds and scores.
    - best_threshold: The value of the best threshold to highlight.
    
    Returns:
    - A styled DataFrame with the entire row of the best threshold highlighted in blue.
    """
    # Define a function to apply the styling
    def apply_highlight(row):
        # Compare if the current row's threshold matches the best threshold
        # If match, return the style for each cell in the row; otherwise, return ''
        return ['background-color: #132E57; color: white' if row['Threshold'] == best_threshold else '' for _ in row]
    
    # Apply the styling function to each row
    return df.style.apply(apply_highlight, axis=1)

def adjust_and_sort_cutoffs(df_cutoffs, min_score, max_score):
    # Ensure DataFrame is sorted by 'Total Score' before proceeding
    df_cutoffs.sort_values(by='Total Score', inplace=True)
    
    # Approximation based on current highest and lowest scores
    current_min_score = df_cutoffs['Total Score'].min()
    current_max_score = df_cutoffs['Total Score'].max()

    # Calculate the proportionate threshold if needed
    if current_min_score > min_score:
        # Approximate the threshold for min_score
        # Assuming linear proportion for simplicity
        min_threshold_approx = df_cutoffs.iloc[0]['Threshold'] * (min_score / current_min_score)
        df_cutoffs = pd.concat([pd.DataFrame({'Threshold': [min_threshold_approx], 'Total Score': [min_score]}), df_cutoffs], ignore_index=True)

    if current_max_score < max_score:
        # Approximate the threshold for max_score
        # Assuming linear proportion for simplicity
        max_threshold_approx = df_cutoffs.iloc[-1]['Threshold'] * (max_score / current_max_score)
        df_cutoffs = pd.concat([df_cutoffs, pd.DataFrame({'Threshold': [max_threshold_approx], 'Total Score': [max_score]})], ignore_index=True)

    # Sort the DataFrame by 'Total Score' in descending order for final presentation
    df_cutoffs.sort_values(by='Total Score', ascending=False, inplace=True)

    return df_cutoffs

def create_score_bins(df_cutoffs, max_score):
    """
    Creates and assigns bins for the Total Score in df_cutoffs, correcting the bin ranges to ensure proper inclusion.
    
    Parameters:
    - df_cutoffs: DataFrame containing the 'Threshold' and 'Total Score' columns.
    - max_score: The maximum score defined for the scoring range.

    Returns:
    - df_cutoffs with an additional column 'Score Bin' indicating the bin for each score.
    """
    # Ensure df_cutoffs is sorted by 'Total Score'
    df_cutoffs_sorted = df_cutoffs.sort_values(by='Total Score')

    # Create bins based on unique 'Total Score' values
    total_scores = df_cutoffs_sorted['Total Score'].unique()

    # Check if total_scores is empty
    if len(total_scores) == 0:
        print("Warning: No scores available to create bins.")
        return df_cutoffs_sorted  # Return the unmodified DataFrame or handle this scenario as needed

    bins = [(total_scores[i], total_scores[i+1]) for i in range(len(total_scores)-1)]
    # Adjust the last bin to ensure it includes or excludes the max_score appropriately
    if total_scores[-1] < max_score:
        bins.append((total_scores[-1], max_score))
    else:
        # If the last unique score is equal to or greater than max_score, adjust accordingly
        bins[-1] = (bins[-1][0], max_score)

    # Generate bin labels
    bin_labels = [f"[{bin[0]} - {bin[1]})" for bin in bins[:-1]]
    # Adjust the label for the last bin to include the maximum score
    bin_labels.append(f"[{bins[-1][0]} - {bins[-1][1]})")

    # Assign bins to 'Total Score'
    df_cutoffs_sorted['Score Bin'] = pd.cut(df_cutoffs_sorted['Total Score'],
                                            bins=[b[0] for b in bins] + [max_score],  # Include max_score as an edge for the last bin
                                            labels=bin_labels,
                                            include_lowest=True,
                                            right=False)  # right=False to include the left edge
    
    # Create a new column based on the condition
    max_score_str = str(max_score)
    df_cutoffs_sorted['Total Score Bin'] = np.where(pd.isna(df_cutoffs_sorted['Score Bin']), f"[{max_score_str}, {max_score_str} + error)", df_cutoffs_sorted['Score Bin'])
    df_cutoffs_sorted = df_cutoffs_sorted[['Threshold','Total Score Bin']]

    return df_cutoffs_sorted

def assign_decisions(df_cutoffs, best_threshold):
    """
    Assigns decisions to each score in df_cutoffs based on a specified threshold.

    Parameters:
    - df_cutoffs: DataFrame containing the 'Total Score' column.
    - threshold: The score threshold for decision making.

    Modifies the DataFrame to include:
    - A new column 'Decision' indicating 'Approve', 'Unsure', or 'Reject' based on the threshold's relation to the best threshold.
    """
    # Define a function to determine the decision based on the threshold
    def determine_decision(threshold):
        if threshold > best_threshold:
            return 'Approve'
        elif threshold == best_threshold:
            return 'Unsure'
        else:
            return 'Reject'

    # Apply the function to each threshold in 'Threshold' to create the 'Decision' column
    df_cutoffs['Decision'] = df_cutoffs['Threshold'].apply(determine_decision)
    df_cutoffs = df_cutoffs.sort_values(by='Threshold', ascending=False)

    return df_cutoffs

# Updated generate_scorecard function
def generate_scorecard(classification_method, feature_names, X_test, y_test, min_score=300, max_score=850):
    """
    Generates a scorecard from a logistic regression model and highlights the row with the best threshold.
    
    Parameters:
    - classification_method: A trained classification method with a predict_proba method.
    - feature_names: A list of feature names corresponding to the model's coefficients.
    - X: The input features used by the logistic model for prediction.
    - y_test: The actual labels from the test set to calculate ROC curve.
    - min_score: Minimum possible score on the scorecard.
    - max_score: Maximum possible score on the scorecard.
    
    Returns:
    - A DataFrame containing the scorecard.
    - A styled DataFrame with the row of the best threshold highlighted.
    """
    # Attempt to extract feature importances or coefficients if available
    try:
        if hasattr(classification_method, 'coef_'):
            weights = classification_method.coef_[0]
            intercept = classification_method.intercept_[0] if hasattr(classification_method, 'intercept_') else 0
            # Create a DataFrame for coefficients
            coeff_df = pd.DataFrame(weights, columns=['Coefficients'], index=feature_names).reset_index()
            coeff_df.columns = ['Feature Name', 'Coefficients']
            # Create a DataFrame for the intercept and concatenate
            intercept_df = pd.DataFrame({'Feature Name': ['Intercept'], 'Coefficients': [intercept]})
            coeff_df = pd.concat([coeff_df, intercept_df], ignore_index=True)
        elif hasattr(classification_method, 'feature_importances_'):
            weights = classification_method.feature_importances_
            # Assume no intercept for models using feature importances
            intercept_df = pd.DataFrame({'Feature Name': ['Intercept'], 'Coefficients': [0]})
            # Create a DataFrame for feature importances
            coeff_df = pd.DataFrame(weights, columns=['Coefficients'], index=feature_names).reset_index()
            coeff_df.columns = ['Feature Name', 'Coefficients']
            coeff_df = pd.concat([coeff_df, intercept_df], ignore_index=True)
        elif hasattr(classification_method, 'theta_'):
            # Calculate mean differences as importance for GaussianNB
            means = classification_method.theta_
            # Calculate the absolute difference in means between classes for each feature
            mean_differences = np.abs(means[0] - means[1])
            weights = mean_differences
            # Assume no intercept for models using feature importances
            intercept_df = pd.DataFrame({'Feature Name': ['Intercept'], 'Coefficients': [0]})
            # Create a DataFrame for feature importances
            coeff_df = pd.DataFrame(weights, columns=['Coefficients'], index=feature_names).reset_index()
            coeff_df.columns = ['Feature Name', 'Coefficients']
            coeff_df = pd.concat([coeff_df, intercept_df], ignore_index=True) 
        elif hasattr(classification_method, 'named_steps'):
            weights = classification_method.named_steps['sgdclassifier'].coef_[0]
            intercept = classification_method.named_steps['sgdclassifier'].intercept_[0] if hasattr(classification_method, 'intercept_') else 0
            # Create a DataFrame for coefficients
            coeff_df = pd.DataFrame(weights, columns=['Coefficients'], index=feature_names).reset_index()
            coeff_df.columns = ['Feature Name', 'Coefficients']
            # Create a DataFrame for the intercept and concatenate
            intercept_df = pd.DataFrame({'Feature Name': ['Intercept'], 'Coefficients': [intercept]})
            coeff_df = pd.concat([coeff_df, intercept_df], ignore_index=True)
        else:
            print("Model does not provide coefficients or feature importances.")
            return None
    except AttributeError:
        return "This classification method does not support this operation."

    # Calculate min and max sum of coefficients excluding the intercept
    min_coef = coeff_df[coeff_df['Feature Name'] != 'Intercept']['Coefficients'].min()
    max_coef = coeff_df[coeff_df['Feature Name'] != 'Intercept']['Coefficients'].max()

    # Check if min_coef is a singular value (e.g., int, float) or a collection (e.g., list, numpy array)
    if isinstance(min_coef, (int, float)):  # Checks if it's a singular numerical value
        # Code to execute if min_coef is a singular value
        min_sum_coef = min_coef
    else:
        min_sum_coef = min_coef.sum()

    # Check if max_coef is a singular value (e.g., int, float) or a collection (e.g., list, numpy array)
    if isinstance(max_coef, (int, float)):  # Checks if it's a singular numerical value
        # Code to execute if max_coef is a singular value
        max_sum_coef = max_coef
    else:
        max_sum_coef = max_coef.sum()

    # Score calculation for all features
    coeff_df['Score - Calculation'] = (coeff_df['Coefficients'] * (max_score - min_score) / (max_sum_coef - min_sum_coef)).round().astype(int)
    
    # Find the position of the intercept
    n = coeff_df.index[coeff_df['Feature Name'] == 'Intercept'].tolist()[0]
    
    # Update the calculated score of the Intercept
    coeff_df.loc[n, 'Score - Calculation'] = (
        ((coeff_df.loc[n, 'Coefficients'] - min_sum_coef) / 
        (max_sum_coef - min_sum_coef)) * (max_score - min_score) + min_score).round().astype(int)
    
    # Calculate probabilities for the positive class
    probs = classification_method.predict_proba(X_test)[:, 1]
    
    # Calculate FPR, TPR, and thresholds using the actual test labels
    fpr, tpr, threshold = roc_curve(y_test, probs)
    J = tpr - fpr
    ix = np.argmax(J)
    best_thresh = threshold[ix]
    
    # Thresholds table
    df_cutoffs = pd.DataFrame({'Threshold': threshold})
    df_cutoffs['Total Score'] = ((np.log(df_cutoffs['Threshold'] / (1 - df_cutoffs['Threshold'])) - min_sum_coef) * 
                      ((max_score - min_score) / (max_sum_coef - min_sum_coef)) + min_score).round()
    
    # Replace inf with NaN and then drop rows with NaN in 'Total Score'
    df_cutoffs.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_cutoffs.dropna(subset=['Total Score'], inplace=True)
    
    # Round 'Total Score' to whole number and convert to integer, ensuring the scores are finite
    df_cutoffs['Total Score'] = df_cutoffs['Total Score'].round().astype(int)
        
    # Ensure 'Total Score' falls within the specified range and filter out those that don't
    df_cutoffs = df_cutoffs[(df_cutoffs['Total Score'] >= min_score) & (df_cutoffs['Total Score'] <= max_score)]

    # Usage within the generate_scorecard function
    df_cutoffs = adjust_and_sort_cutoffs(df_cutoffs, min_score, max_score)

    # Create score bins
    df_cutoffs = create_score_bins(df_cutoffs, max_score)

    # Create decisions bins
    df_cutoffs = assign_decisions(df_cutoffs, best_thresh)

    # Highlight the best threshold row
    styled_df = highlight_best_threshold(df_cutoffs, best_thresh)
    
    return coeff_df, styled_df

# Note: Ensure that `classification_method`, `feature_names`, `X_test`, and `y_test` are correctly defined before using this function.

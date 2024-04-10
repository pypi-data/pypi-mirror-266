from sklearn.model_selection import train_test_split, cross_validate
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate
import pandas as pd

def perform_analysis(X, y):
    """
    Perform analysis on the input data.

    Parameters:
        X (DataFrame): Input features.
        y (Series): Target variable.
        output_path (str): Path to save the analysis results.

    Returns:
        DataFrame: Cross-validation results for the Logistic Regression classifier.

    Examples:
    ---------

    >>> X, y = load_iris(return_X_y=True)
    >>> X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=123)
    >>> output_path = "analysis_results"
    >>> perform_analysis(X_train, y_train, output_path)
    # This function will perform analysis on the input data X_train and y_train
    # and save the results in the specified output_path directory.

    Notes:
    This function requires pandas, sklearn, and numpy libraries.
    """
    if not isinstance(X, pd.DataFrame) or not isinstance(y, pd.Series):
        raise TypeError("X must be a pandas DataFrame and y must be a pandas Series.")
    
    # Perform one-hot encoding with sparse representation
    X_encoded = pd.get_dummies(X, sparse=True)
    
    # Split the data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.3, random_state=123)  
    
    # Initialize classifiers
    dummy = DummyClassifier()
    lr = LogisticRegression()
    
    # Fit the classifiers
    dummy.fit(X_train, y_train)
    lr.fit(X_train, y_train)
    
    # Evaluate the classifier
    dummy_results = pd.DataFrame(cross_validate(dummy, X_train, y_train, return_train_score=True)).mean().to_frame().T
    dummy_results.columns = ['Fit Time', 'Score Time', 'Test Score', 'Train Score']

    cv_results_lr = pd.DataFrame(cross_validate(lr, X_train, y_train, return_train_score=True)).mean().to_frame().T
    cv_results_lr.columns = ['Fit Time', 'Score Time', 'Test Score', 'Train Score']
    
    viz_df = pd.DataFrame({"features": X_train.columns, "coefficients": lr.coef_[0]})

    return lr, dummy_results, cv_results_lr, viz_df


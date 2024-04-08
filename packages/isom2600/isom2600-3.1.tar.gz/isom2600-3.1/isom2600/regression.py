
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import seaborn as sns
import scipy.stats as stats
import seaborn as sns
from tqdm import notebook
import itertools
from sklearn.metrics import mean_squared_error
import statsmodels.api as sm
import pandas as pd
import numpy as np
# import warnings
# warnings.filterwarnings('ignore')

def fit_linear_reg(X,Y):
    #Fit linear regression model and return SSE and R squared values
    model_k = sm.OLS(Y,sm.add_constant(X)).fit()
    SSE = mean_squared_error(Y,model_k.predict(sm.add_constant(X))) * len(Y)
    R_squared = model_k.rsquared
    adj_R2 = model_k.rsquared_adj
    AIC = model_k.aic
    BIC = model_k.bic
    return SSE, R_squared, adj_R2, AIC, BIC

def best_subset_selection(X, Y):
    k = X.shape[1]
    SSE_list, R_squared_list, adj_R2_list, AIC_list, BIC_list, feature_list = [], [], [], [], [], []
    numb_features = []

    # Looping over k = 1 to k = 11 features in X
    for k in notebook.trange(1, len(X.columns) + 1, desc='Loop...'):

        # Looping over all possible combinations: from 11 choose k
        for combo in itertools.combinations(X.columns, k):
            tmp_result = fit_linear_reg(X[list(combo)], Y)  # Store temp result
            SSE_list.append(tmp_result[0])  # Adds its argument as a single element to the end of a list.
            R_squared_list.append(tmp_result[1])
            adj_R2_list.append(tmp_result[2])
            AIC_list.append(tmp_result[3])
            BIC_list.append(tmp_result[4])
            feature_list.append(combo)
            numb_features.append(len(combo))

            # Store in DataFrame
    df = pd.DataFrame(
        {'numb_features': numb_features, 'SSE': SSE_list, 'R_squared': R_squared_list, 'adj_R2': adj_R2_list,
         'AIC': AIC_list, 'BIC': BIC_list, 'features': feature_list})
    return df

def forward_selection(X, Y):
    k = X.shape[1]

    remaining_features = list(X.columns.values)
    features = []
    SSE_list, R_squared_list, adj_R2_list, AIC_list, BIC_list = [np.inf], [np.inf], [np.inf], [np.inf], [np.inf]  # Due to 1 indexing of the loop...
    features_list = dict()

    for i in range(1, k + 1):
        best_SSE = np.inf

        for combo in itertools.combinations(remaining_features, 1):

            tmp_result = fit_linear_reg(X[list(combo) + features], Y)  # Store temp result

            if tmp_result[0] < best_SSE:
                best_SSE = tmp_result[0]
                best_R_squared = tmp_result[1]
                best_adj_R2 = tmp_result[2]
                best_AIC = tmp_result[3]
                best_BIC = tmp_result[4]
                best_feature = combo[0]

        # Updating variables for next loop
        features.append(best_feature)
        remaining_features.remove(best_feature)

        # Saving values for plotting
        SSE_list.append(best_SSE)
        R_squared_list.append(best_R_squared)
        adj_R2_list.append(best_adj_R2)
        AIC_list.append(best_AIC)
        BIC_list.append(best_BIC)
        features_list[i] = features.copy()

    result = {'SSE': SSE_list,
              'R_squared': R_squared_list,
              'adj_R2': adj_R2_list,
              'AIC': AIC_list,
              'BIC': BIC_list,
              'features': features_list}

    return result

def backward_selection(X, Y):
    k = X.shape[1]

    remaining_features = list(X.columns.values)
    SSE_list, R_squared_list, adj_R2_list, AIC_list, BIC_list = [], [], [], [], []  # Due to 1 indexing of the loop...

    features_list = dict()

    for i in range(1, k + 1):
        best_SSE = np.inf

        for combo in itertools.combinations(remaining_features, k + 1 - i):

            temp_result = fit_linear_reg(X[list(combo)], Y)  # Store temp result

            if temp_result[0] < best_SSE:
                best_SSE = temp_result[0]
                best_R_squared = temp_result[1]
                best_adj_R2 = temp_result[2]
                best_AIC = temp_result[3]
                best_BIC = temp_result[4]
                best_feature = combo

        # Updating variables for next loop
        remaining_features = best_feature

        # Saving values for plotting
        SSE_list.append(best_SSE)
        R_squared_list.append(best_R_squared)
        adj_R2_list.append(best_adj_R2)
        AIC_list.append(best_AIC)
        BIC_list.append(best_BIC)
        features_list[i] = best_feature

    result = {'SSE': SSE_list,
              'R_squared': R_squared_list,
              'adj_R2': adj_R2_list,
              'AIC': AIC_list,
              'BIC': BIC_list,
              'features': features_list}

    return result

def stepwise_selection(X, y,
                       initial_list=[],
                       threshold_in=0.01,
                       threshold_out = 0.05,
                       verbose=True):
    """ Perform a forward-backward feature selection
    based on p-value from statsmodels.api.OLS
    Arguments:
        X - pandas.DataFrame with candidate features
        y - list-like with the target
        initial_list - list of features to start with (column names of X)
        threshold_in - include a feature if its p-value < threshold_in
        threshold_out - exclude a feature if its p-value > threshold_out
        verbose - whether to print the sequence of inclusions and exclusions
    Returns: list of selected features
    Always set threshold_in < threshold_out to avoid infinite looping.
    See https://en.wikipedia.org/wiki/Stepwise_regression for the details
    """
    included = list(initial_list)
    while True:
        changed=False
        # forward step
        excluded = list(set(X.columns)-set(included))
        new_pval = pd.Series(index=excluded)
        for new_column in excluded:
            model = sm.OLS(y, sm.add_constant(pd.DataFrame(X[included+[new_column]]))).fit()
            new_pval[new_column] = model.pvalues[new_column]
        best_pval = new_pval.min()
        if best_pval < threshold_in:
            best_feature = new_pval.idxmin()
            included.append(best_feature)
            changed=True
            if verbose:
                print('Add  {:30} with p-value {:.6}'.format(best_feature, best_pval))

        # backward step
        model = sm.OLS(y, sm.add_constant(pd.DataFrame(X[included]))).fit()
        # use all coefs except intercept
        pvalues = model.pvalues.iloc[1:]
        worst_pval = pvalues.max() # null if pvalues is empty
        if worst_pval > threshold_out:
            changed=True
            worst_feature = pvalues.idxmax()
            included.remove(worst_feature)
            if verbose:
                print('Drop {:30} with p-value {:.6}'.format(worst_feature, worst_pval))
        if not changed:
            break
    return included
def outlier(dataframe,model,Type='all'):
    A = dataframe.copy()
    A = A.dropna()
    A.index = range(1,A.shape[0]+1)
    studentized_residuals = model.get_influence().resid_studentized_internal
    A["ExpectProfit"] = model.fittedvalues
    if Type == 'neg':
        return(A[["Location","ExpectProfit","Profit"]][studentized_residuals<-2])
    elif Type == 'posi':
        return(A[["Location","ExpectProfit","Profit"]][studentized_residuals>2])
    else:
        return(A[["Location","ExpectProfit","Profit"]][np.abs(studentized_residuals)>2])

def getvif(X):
    X = sm.add_constant(X)
    vif = pd.DataFrame()
    vif["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    vif["Predictors"] = X.columns
    return(vif.drop(index = 0).round(2))
def four_in_one(dataframe,model):
    fitted_y = model.fittedvalues
    studentized_residuals = model.get_influence().resid_studentized_internal
    plt.figure(figsize=(10,10))
    ax1 = plt.subplot(221)
    stats.probplot(studentized_residuals, dist="norm", plot=plt)
    ax1.set_title('Normal Q-Q')
    ax1.set_xlabel('Normal Quantiles')
    ax1.set_ylabel('Studentized Residuals');

    ax2 = plt.subplot(222)
    ax2.hist(studentized_residuals)
    ax2.set_xlabel('Studentized Residuals')
    ax2.set_ylabel('Count')
    ax2.set_title('Histogram')

    ax3 = plt.subplot(223)
    t = range(dataframe.shape[0])
    ax3.scatter(t, studentized_residuals)
    ax3.set_xlabel('Observation order')
    ax3.set_ylabel('Residuals')
    ax3.set_title('Time series plot of studentized residuals')

    ax4 = plt.subplot(224)
    ax4 = sns.residplot(x=fitted_y, y=studentized_residuals,
                              lowess=True,
                              scatter_kws={'alpha': 0.5},
                              line_kws={'color': 'red', 'lw': 1, 'alpha': 0.8})
    ax4.set_title('Internally Studentized Residuals vs Fitted values')
    ax4.set_xlabel('Fitted values')
    ax4.set_ylabel('Studentized Residuals');
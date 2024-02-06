from pygam import LinearGAM, s
import pandas as pd
import numpy as np
import pickle


def filter_outliers(df):
    # not used
    Q1 = df['Per capita personal income'].quantile(0.01)
    Q3 = df['Per capita personal income'].quantile(0.99)
    IQR = Q3 - Q1

    # Define bounds for outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Filter out outliers
    df = df[(df['Per capita personal income'] >= lower_bound) & (df['Per capita personal income'] <= upper_bound)]
    df['Weighted_Score_Normalized'] = round(df.Weighted_Score_Normalized,2)
    
    return df

def fit_gam(df):
    # Fit a GAM model
    gam = LinearGAM(s(0, n_splines=20, lam=2, constraints='monotonic_dec'))
    gam.fit(df[['Per capita personal income']], df['Weighted_Score_Normalized'])
    # Get the summary of the GAM model
    #gam_summary = gam.summary()
    # Extract the R-squared (R2) value from the summary
    pseudo_r2_value = gam.statistics_['pseudo_r2']['explained_deviance']
    #print(gam.summary())
    #print(pseudo_r2_value)
    # Generate predictions and intervals as before
    x_pred = pd.DataFrame({'Per capita personal income': np.linspace(df['Per capita personal income'].min(), df['Per capita personal income'].max(), 500)})
    y_pred = gam.predict(x_pred)
    y_intervals = gam.prediction_intervals(x_pred, width=0.8)
    y_intervals[:, 0] = np.maximum(y_intervals[:, 0], 0)  # Set lower bounds to 0 if they are below 0
    
    # Plot the residuals
    #residuals = df['Weighted_Score_Normalized'] - gam.predict(df[['Per capita personal income']])
    #plt.figure(figsize=(10, 6))
    #plt.scatter(x, residuals, facecolors='none', edgecolors='r')
    #plt.axhline(y=0, color='k', linestyle='--')
    #plt.xlabel('Feature Value')
    #plt.ylabel('Residuals')
    #plt.title('Residual Plot for GAM')
    #plt.grid(True)
    # Save the plot
    #plt.savefig('gam_residuals.png')
# Assuming x_pred is a pandas DataFrame and the rest are NumPy arrays or scalars
    with open("models/x_pred.pkl", "wb") as f:
        pickle.dump(x_pred, f)

    with open("models/y_pred.pkl", "wb") as f:
        pickle.dump(y_pred, f)

    with open("models/y_intervals.pkl", "wb") as f:
        pickle.dump(y_intervals, f)

    with open("models/pseudo_r2_value.pkl", "wb") as f:
        pickle.dump(pseudo_r2_value, f)

    print("All output saved to models/ using pickle.")
    
    return x_pred, y_pred, y_intervals, pseudo_r2_value
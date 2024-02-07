from pygam import LinearGAM, s
import pandas as pd
import numpy as np

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


def fit_gam(df_path = "data/processed/df_summary_final.pickle"):
    df = pd.read_pickle(df_path)
    
    # Fit a GAM model
    gam = LinearGAM(s(0, n_splines=20, lam=2, constraints='monotonic_dec'))
    gam.fit(df[['Per capita personal income']], df['Weighted_Score_Normalized'])
    
    print(gam.summary())
    pseudo_r2_value = gam.statistics_['pseudo_r2']['explained_deviance']
    print(pseudo_r2_value)
    
    df_pred = pd.DataFrame({'Per capita personal income': np.linspace(df['Per capita personal income'].min(), df['Per capita personal income'].max(), 500)})
    y_pred = gam.predict(df_pred)

    y_intervals = gam.prediction_intervals(df_pred, width=0.8)
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

    # Combining y_pred and y_intervals with x_pred DataFrame
    df_pred['y_pred'] = y_pred
    df_pred['lower_interval'] = y_intervals[:, 0]
    df_pred['upper_interval'] = y_intervals[:, 1]
    
    # Add pseudo R² as an attribute to the DataFrame (optional)
    df_pred.attrs['pseudo_r2_value'] = pseudo_r2_value
    print(df_pred.head())
    # Save combined DataFrame using pickle

    df_pred.to_pickle("models/gam_model_output.pkl")
    print("All output saved to models/gam_model_output.pkl.")

    return df_pred


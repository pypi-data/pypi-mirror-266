# simulations.py
import numpy as np
import pandas as pd

def generate_cov_matrix(n, structure='diagonal', block_size=None, rho=0.9):
    """
    Generate covariance matrices of various structures.

    Parameters:
    - n: The dimension of the covariance matrix.
    - structure: The structure of the matrix ('diagonal', 'block_diagonal', 'toeplitz', 'ar').
    - block_size: The size of each block for 'block_diagonal' structure. Ignored for other structures.
    - rho: The correlation coefficient for 'ar' (AutoRegressive) and 'toeplitz' structures.

    Returns:
    - A numpy array representing the covariance matrix.
    """
    if structure == 'diagonal':
        # Generate a diagonal matrix with variance (pi/3)^2 on the diagonal
        return np.diag(np.full(n, np.power(np.pi/3, 2)))
    
    elif structure == 'block_diagonal':
        if block_size is None:
            raise ValueError("Block size must be specified for block_diagonal structure.")
        # Calculate number of blocks
        num_blocks = n // block_size
        block = np.diag(np.full(block_size, np.power(np.pi/3, 2)))
        # Generate block diagonal matrix
        return np.block([[block if i == j else np.zeros((block_size, block_size)) for j in range(num_blocks)] for i in range(num_blocks)])
    
    elif structure == 'toeplitz':
        # Generate a Toeplitz matrix where each descending diagonal from left to right is constant.
        return np.power(np.pi/3, 2) * rho ** np.abs(np.subtract.outer(np.arange(n), np.arange(n)))
    
    elif structure == 'ar':
        # Generate an AR(rho) covariance matrix
        ar_cov_matrix = np.power(np.pi/3, 2) * rho ** np.abs(np.subtract.outer(np.arange(n), np.arange(n)))
        return ar_cov_matrix
    
    else:
        raise ValueError("Invalid structure specified.")


 
def execute_conditional_simulations(n, Sj, Sjc, xjc, mean_vector, covMat):
    # Define the conditional multivariate normal distribution function
    def conditional_mvn(mean, cov, known_indices, known_values):
        known_values = np.array(known_values).reshape(-1)
        unknown_indices = np.setdiff1d(np.arange(len(mean)), known_indices)
        sigma_known_known = cov[np.ix_(known_indices, known_indices)]
        sigma_known_unknown = cov[np.ix_(known_indices, unknown_indices)]
        sigma_unknown_known = cov[np.ix_(unknown_indices, known_indices)]
        sigma_unknown_unknown = cov[np.ix_(unknown_indices, unknown_indices)]
        mu_known = mean[known_indices]
        mu_unknown = mean[unknown_indices]
        diff = (known_values - mu_known).reshape(-1, 1)
        mu_cond = mu_unknown + np.dot(sigma_unknown_known, np.linalg.inv(sigma_known_known)).dot(diff).flatten()
        sigma_cond = sigma_unknown_unknown - np.dot(sigma_unknown_known, np.linalg.inv(sigma_known_known)).dot(sigma_known_unknown)
        return np.random.multivariate_normal(mu_cond, sigma_cond)
    
    # Define the conditional simulation function
    def condSim(n, Sj, Sjc, xjc, mean_vector, covMat):
        d = len(covMat)
        df_samples = pd.DataFrame(index=np.arange(n), columns=np.arange(d))
        for i in range(n):
            if len(Sjc) == d:
                df_samples.iloc[i, :] = xjc
            elif len(Sjc) > 0:
                xjc_array = np.array(xjc)
                simulated_values = conditional_mvn(mean_vector, covMat, Sjc, xjc_array)
                df_samples.iloc[i, Sjc] = xjc_array
                if len(Sj) > 0:
                    df_samples.iloc[i, Sj] = simulated_values
            else:
                df_samples.iloc[i, :] = np.random.multivariate_normal(mean_vector, covMat)
        return df_samples.to_numpy().tolist()

    # Execute the conditional simulation
    simulated_values = condSim(n, Sj, Sjc, xjc, mean_vector, covMat)
    return simulated_values



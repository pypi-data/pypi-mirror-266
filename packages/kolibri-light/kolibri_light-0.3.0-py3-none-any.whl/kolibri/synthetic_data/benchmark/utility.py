import numpy as np
import pandas as pd
from kolibri.synthetic_data.benchmark.utils import bin_data


def fidelity(real_data, synthetic_data, c = 10, k = 1, algorithm='tvd'):
    """

    Args:
        real_data:
        synthetic_data:
        c:
        k: interactions, 1-way, 2-ways, 3-ways. Can have 1, 2, 3 values
        algorithm: 'tvd'=Total Variational Distance

    Returns:

    """
    # build grid of all cross-combinations
    cols = real_data.columns


    interactions = pd.DataFrame(np.array(np.meshgrid(cols, cols, cols)).reshape(3, len(cols)**3).T)
    interactions.columns = ['dim1', 'dim2', 'dim3']
    if k == 1:
        interactions = interactions.loc[(interactions['dim1']==interactions['dim2']) & (interactions['dim2']==interactions['dim3'])]
    elif k == 2:
        interactions = interactions.loc[(interactions['dim1']<interactions['dim2']) & (interactions['dim2']==interactions['dim3'])]
    elif k == 3:
        interactions = interactions.loc[(interactions['dim1']<interactions['dim2']) & (interactions['dim2']<interactions['dim3'])]
        # limit calculations to max 1000 interactions
        interactions = interactions.sample(n=min(1_000, len(interactions)))
    else:
        raise('k>3 not supported')

    results = []
    if algorithm=='tvd':
        [dt1_bin, dt2_bin] = bin_data(real_data, synthetic_data, c = c)

        for idx in range(interactions.shape[0]):
            row = interactions.iloc[idx]
            val1 = dt1_bin[row.dim1] + dt1_bin[row.dim2] + dt1_bin[row.dim3]
            val2 = dt2_bin[row.dim1] + dt2_bin[row.dim2] + dt2_bin[row.dim3]
            freq1 = val1.value_counts(normalize=True).to_frame(name='p1')
            freq2 = val2.value_counts(normalize=True).to_frame(name='p2')
            freq = freq1.join(freq2, how='outer').fillna(0.0)
            p1 = freq['p1']
            p2 = freq['p2']
            tvd = np.sum(np.abs(p1 - p2)) / 2
            acc = 1 - tvd
            out = pd.DataFrame({
              'k': f"{k=}",
              'dim1': [row.dim1],
              'dim2': [row.dim2],
              'dim3': [row.dim3],
              'tvd': [tvd],
              'accuracy': [acc],
            })
            results.append(out)

    return pd.concat(results)
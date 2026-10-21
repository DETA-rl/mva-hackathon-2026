import numpy as np
from scipy import stats
def power(n, d, alpha=0.05):
    df = 2*n-2; nc = d*np.sqrt(n/2)
    tc = stats.t.ppf(1-alpha/2, df)
    return 1 - stats.nct.cdf(tc, df, nc) + stats.nct.cdf(-tc, df, nc)
def n_for(d, pw=0.8, alpha=0.05):
    n=2
    while power(n,d,alpha)<pw: n+=1
    return n
ns=[5,10,20,40,80]
print("Illustrative two-arm t-test, alpha 0.05 two-sided. Effect d = standardized difference (difference / SD).")
print("n per arm | " + " | ".join(f"d={d}" for d in [0.3,0.5,0.8]))
for n in ns:
    print(f"{n:9d} | " + " | ".join(f"{power(n,d)*100:5.1f}%" for d in [0.3,0.5,0.8]))
print("n per arm needed for 80% power:", {d:n_for(d) for d in [0.3,0.5,0.8]})

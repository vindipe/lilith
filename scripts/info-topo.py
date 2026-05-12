import pandas as pd

df = pd.read_csv("results/info-topo/scale-free-l/kollaps-df.csv")

print(df['k_latency_diff_%'].mean())
print(df['k_latency_diff_%'].std())
print(df['k_throughput_diff_%'].mean())
print(df['k_throughput_diff_%'].std())

#full-mesh
    #lat-mean,  2.3 / 5.2 / 6.5
    #lat-std,   1 / 3 / 3.5
    #thr-mean   -17.7 / -20.7 / -55.4
    #thr-std    20.2 / 18.5 / 10.9
#fat-tree
    #lat-mean,  133.8 / 119.7
    #lat-std,   171.2 / 113.5
    #thr-mean,  -65 / -66
    #thr-std,   36.7 / 34
#scale-free
    #lat-mean,  44.5 / 42.9
    #lat-std,   158.7 / 133
    #thr-mean,  -31.4 / -34
    #thr-std,   30.7 / 28.5
#hypercube
    #lat-mean,  78 / 76.9
    #lat-std,   173.7 / 141
    #thr-mean,  -40.6 / -44.4
    #thr-std,   37.8 / 34.5
#torus
    #lat-mean,  119 / 101.9
    #lat-std,   151.9 / 144.8
    #thr-mean,  -53.9 / -52.7
    #thr-std,   42.47 / 38.3
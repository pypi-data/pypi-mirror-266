
Sparse Data Observers (**SDO**) is an unsupervised learning
approach developed to cover the need for fast, highly interpretable and
intuitively parameterizable anomaly detection. Its extension, **SDOclust**, 
performs clustering while preserving the simplicity and applicability of the original approach. 

SDO and SDOclust are powerful options when statistical estimates
are representative and feature spaces conform distance-based analysis.
Their main characteristics are: lightweight, intuitive, self-adjusted, noise-
resistant, able to extract non-convex clusters (SDOclust), and built on robust 
parameters and interpretable models. 

Feasibility and rapid integration into real-world applications are the core goals 
behind SDO and SDOclust, which can work on most data scenarios without parameter 
adjustment (simply using the default parameterization).

## Installation and dependecies

sdo can be installed from PyPI using

        pip3 install sdoclust

or directly from our GitHub repository:

        pip3 install git+https://github.com/CN-TU/pysdoclust

sdo requires de following packages:

- numpy
- math
- scipy
- sklearn

## Examples of usage

## SDO

        import numpy as np
        np.random.seed(1)

        # Generate data
        from sklearn import datasets
        x, y = datasets.make_circles(n_samples=5000, factor=0.3, noise=0.1)

        # SDO outlier scoring
        import sdoclust as sdo
        s = sdo.SDO().fit_predict(x)

        # plotting results
        import matplotlib.pyplot as plt
        fig = plt.figure()
        plt.scatter(x[:,0],x[:,1], s=10, cmap='coolwarm', c=s)
        plt.colorbar(ticks=[np.min(s), np.max(s)])
        plt.title('SDO outlierness scores')
        plt.show()

![](tests/sdo.png)

## SDOclust

        import numpy as np
        np.random.seed(1)

        # Generate data
        from sklearn import datasets
        x, y = datasets.make_circles(n_samples=5000, factor=0.3, noise=0.1)

        # SDOclust clustering
        import sdoclust as sdo
        p = sdo.SDOclust().fit_predict(x)

        # plotting results
        import matplotlib.pyplot as plt
        fig = plt.figure()
        plt.scatter(x[:,0],x[:,1], s=10, cmap='coolwarm', c=p)
        plt.title('SDOclust clustering')
        plt.show()

![](tests/sdoclust.png)

## Application notes

SDO and SDOclust obtain good performances without modifying the default parameterization in most applications, but may require adjustment in some cases: typically, when datasets have very few elements, when clusters are overlapping or in cases with many under-represented clusters. 

Main SDO parameters are:

- *x*, which establishes the number of closest observers to evaluate each data point.
- *qv*, which sets a robust threshold for removing *idle* observers.
- *k*, which fixes de number of observers in the model

        mdl = sdo.SDO(x=5, qv=0.3, k=500)

Additionally, SDOclust also incorporates:


- *zeta*, which sets a trade-off between locality and globality for cutting-off graph edges thresholds.
- *chi*, which defines the *chi*-closest observer of any given observer to decide cutting-off graph edges thresholds.
- *e* sets the minimum number of observers that a cluster can have.

        mdl = sdo.SDOclust(zeta=0.6, chi=10, e=3)

[1] and [2] provide further explanations on SDO and SDOclust parameters.

## Citation

If you use SDO or SDOclust in your research, please cite our publications:

### SDO

[1] Iglesias, F., Zseby, T., Hartl, A., Zimek, A. (2023). SDOclust: Clustering with Sparse Data Observers. In: Pedreira, O., Estivill-Castro, V. (eds) Similarity Search and Applications. SISAP 2023. Lecture Notes in Computer Science, vol 14289. Springer, Cham. https://doi.org/10.1007/978-3-031-46994-7_16

        @INPROCEEDINGS{SDO2018,
            author    = {F{\'e}lix Iglesias and Tanja Zseby and Alexander Hartl and Arthur Zimek},
            booktitle={2018 IEEE International Conference on Data Mining Workshops (ICDMW)}, 
            title={Outlier Detection Based on Low Density Models}, 
            year={2018},
            volume={},
            number={},
            pages={970-979},
            doi={10.1109/ICDMW.2018.00140}}	
        }


### SDOclust

[2] Iglesias, F., Zseby, T., Zimek, A., "Outlier Detection Based on Low Density Models," 2018 IEEE International Conference on Data Mining Workshops (ICDMW), Singapore, 2018, pp. 970-979, doi: 10.1109/ICDMW.2018.00140. keywords: {Observers;Anomaly detection;Clustering algorithms;Data models;Statistical analysis;Decision making;Complexity theory;outlier analysis;eager learning;machine learning model},


        @InProceedings{SDOclust2023,
            title     = {SDOclust: Clustering with Sparse Data Observers},
            author    = {F{\'e}lix Iglesias and Tanja Zseby and Arthur Zimek},
            editor    = {{\'O}scar Pedreira and Vladimir Estivill-Castro",
            booktitle = {Similarity Search and Applications},
            year      = {2023},
            publisher = {Springer Nature Switzerland},
            address   = {Cham},
            pages     = {185--199},
            doi       = {https://doi.org/10.1007/978-3-031-46994-7\_16}
        }


## Others

- Experiments conducted in [2] are available to download in: 
Iglesias Vázquez, F.: *SDOclust Evaluation Tests (Jun 2023)*. [https://doi.org/10.48436/3q7jp-mg161](https://doi.org/10.48436/3q7jp-mg161)

- The observers-partitioning task in SDOclust is based on the Graph-Based clustering work of Dani El-Ayyass: [https://github.com/dayyass/graph-based-clustering](https://github.com/dayyass/graph-based-clustering)

- An alternative implementation of SDO (only for outlier detection) by Alexander Hartl is in: [https://github.com/CN-TU/pysdo](https://github.com/CN-TU/pysdo)

- A version of SDO for streaming data (SDOstream) is included in the dSalmon package: [https://pypi.org/project/dSalmon/](https://pypi.org/project/dSalmon/)

- Outlier thresholding (i.e., binary/crips labels for outlier/inlier) can be performed externally with multiple algorithms. The pythresh package offers multiple options: [https://github.com/KulikDM/pythresh](https://github.com/KulikDM/pythresh)

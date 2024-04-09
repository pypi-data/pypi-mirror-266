
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/dwyl/esta/issues)

# pycv: Python Cross Validation Library

The Python Cross Validation Library (`pycv`) assembles a set of cross validation methods to mitigate dataset shift.

Dataset shift corresponds to a scenario where the training and test sets have different distributions and encompass several representations (i.e., covariate shift, prior probability
shift, concept shift, internal covariate shift). An example of dataset shift (namely covariate shift) is depicted in Figure 1, where one class concentrates low feature values in training
and high feature values in testing.

![alt text](https://github.com/DiogoApostolo/pyCV/blob/main/images/datasetShift.png?raw=true)
*Figure 1: Example of covariate shift: when analyzing the training dataset, it would appear the minority class (blue) only has values below 6, and the majority class (red) has values above 6. Although in the original dataset, this is not the case.*


Cross validation (CV) is a common method to split a dataset into different training and testing partitions. Nonetheless, the standard CV can induce dataset shift in this division. Other CV variants try to overcome this by splitting the data more carefully. Despite this, to our knowledge, there is no package that implements these methods in a ready-to-use fashion. As a result, many works use the most basic type of CV, which can induce a shift in the data and lead to unreliable results.

To mitigate this gap, the (`pycv`) library currently includes 4 Cross Validation Algorithms aimed at mitigating dataset shift: SCV, DBSCV, DOBSCV and MSSCV

#### SCV
SCV is an improvement over the basic CV which guarantees that the training and testing sets have the same percentages of samples per class as in the original dataset so that the prior probability shift is avoided, however this algorithm does not actively mitigate covariate shift.


#### DBSCV
Introduced in [[1]](https://doi.org/10.1080/095281300146272), DBSCV is a CV variant for addressing covariate shift. This method attempts to separate the data into folds by attributing to each fold a similar observation to the one attributed to a previous fold (Figure 2). In such a way, the distribution of each fold will be more similar when compared to SCV.

![alt text](https://github.com/DiogoApostolo/pyCV/blob/main/images/DBSCV_example.png?raw=true)
*Figure 2: Example of DBSCV for two folds: for each class (blue and red), a starting sample (0 and 1) is chosen and assigned to the first fold, then the closest examples (2 and 3) are chosen and assigned to the next fold. This process is repeated until there are no samples left.*

#### DOBSCV
DOBSCV is an optimized version of DBSCV  proposed in [[2]](https://pubmed.ncbi.nlm.nih.gov/24807526/). While both algorithms are similar in their goal to reduce covariate shift by distributing samples of the same class as evenly as possible between folds, DOBSCV is less sensitive to random choices since, after assigning a sample to each of the $k$ folds, it picks a new random sample to restart the process (Figure 3). 

![alt text](https://github.com/DiogoApostolo/pyCV/blob/main/images/DOBSCV_example.png?raw=true)
*Figure 3: Example of DOBSCV for two folds: for each class (blue and red), a starting sample (0 and 1) is chosen and assigned to the first fold, then the closest examples (2 and 3) are chosen and assigned to the next fold. As all the folds have been assigned a sample, a new starting point is randomly chosen (5 and 8), and the process is repeated until all folds have been assigned a sample again.*

#### MSSCV
MSSCV can be considered a baseline [[2]](https://pubmed.ncbi.nlm.nih.gov/24807526/), corresponding to the opposite version of DBSCV. Instead of assigning the closest sample to the next fold, it assigns the most distant (Figure 4). Each fold will be as different as possible, which may cause an increase in covariate shift but also provide more variability of samples.

![alt text](https://github.com/DiogoApostolo/pyCV/blob/main/images/MSSCV_example.png?raw=true)
*Figure 4: Example of MSSCV for two folds: for each class (blue and red), a starting sample (0 and 1) is chosen and assigned to the first fold, then the most distant examples (8 and 9) are chosen and assigned to the next fold. This process is repeated until there are no samples left.*


## Usage Example:

The `originalDatasets` folder contains some datasets with binary problems. The `CrossValidation.py` module implements the CrossValidation algorithms.
To run the cross validation algorithms, the `CrossValidation` class is instantiated and the results may be obtained as follows:

```python
from pycv_crossvalidation import CrossValidation

CV = CrossValidation.CrossValidation("originalDatasets/61_iris.arff",distance_func="default",file_type="arff")



#Partition the dataset using SCV
SCV_folds,SCV_folds_y,SCV_folds_inx=CV.SCV(foldNum=5)

#Partition the dataset using DBSCV
DBSCV_folds,DBSCV_folds_y,DBSCV_folds_inx=CV.DBSCV(foldNum=5)

#Partition the dataset using MSSCV
MSSCV_folds,MSSCV_folds_y,MSSCV_folds_inx=CV.MSSCV(foldNum=5)

#Partition the dataset using DOBSCV
DOBSCV_folds,DOBSCV_folds_y,DOBSCV_folds_inx=CV.DOBSCV(foldNum=5)



#Write the partitions into arff files
CV.write_folds(SCV_folds,SCV_folds_y,"abalone_3_vs_11-SCV","test_CV/")
CV.write_folds(DBSCV_folds,DBSCV_folds_y,"abalone_3_vs_11-DBSCV","test_CV/")
CV.write_folds(MSSCV_folds,MSSCV_folds_y,"abalone_3_vs_11-MSSCV","test_CV/")
CV.write_folds(DOBSCV_folds,DOBSCV_folds_y,"abalone_3_vs_11-DOBSCV","test_CV/")
```

## Developer notes:
To submit bugs and feature requests, report at [project issues](https://github.com/DiogoApostolo/pyCV/issues).

## Licence:
The project is licensed under the MIT License - see the [License](https://github.com/DiogoApostolo/pyCV/blob/main/LICENSE) file for details.

## References:

[[1]](https://doi.org/10.1080/095281300146272) Xinchuan Zeng and Tony R. Martinez. Distribution-balanced stratified cross-validation
for accuracy estimation. Journal of Experimental & Theoretical Artificial Intelligence,
12(1):1–12, 2000. doi: 10.1080/095281300146272. URL https://doi.org/10.1080/095281300146272.

[[2]](https://pubmed.ncbi.nlm.nih.gov/24807526/) Jose Garc ́ıa Moreno-Torres, Jos ́e A. Saez, and Francisco Herrera. Study on the impact of
partition-induced dataset shift on k-fold cross-validation. IEEE Transactions on Neural
Networks and Learning Systems, 23(8):1304–1312, 2012b. doi: 10.1109/TNNLS.2012.2199516.


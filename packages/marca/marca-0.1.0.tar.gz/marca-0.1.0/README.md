# Modular Association Rule for Classification Algorithms (MARCA)

MARCA is a toolkit for classification based on association rules. It is a modular framework that allows the user to choose the best algorithms for each step of the classification process. The toolkit is implemented in Python and is available under the MIT license. 

## Installation

To install the toolkit, you can use the following command:

```bash
pip install marca
```

## Usage

```python
from marca.extract import Apriori
import numpy as np

# Extract association rules
data = np.array([[1,3,6],
                 [1,4,6],
                 [1,4,5],
                 [2,3,5],
                 [1,4,5]])
x, y = data[:, :-1], data[:, -1]

extractor = Apriori(support=0.1, confidence=0.5, max_len=5)
rules = extractor.fit(x, y)

rules.to_csv('Rules.csv')
```


---
## Algorithms implemented

### Extraction
- Apriori
- AprioriT
- AprioriC
- FP-Growth
- MSApriori
- MSAprioriPartitioned

### Ranking
- CBA
- Borda (Mean, Median, L2, Geometric)
- Topsis
- WSM
- WPM
- Bouker
- BTL

### Pruning
- M1
- Dynamic 
- Coverage

### Classification
- CBA (OrdinalClassification)
- Probability
- RankedBased
- Voting

### Interest Measures implemented
- Accuracy
- Added_value
- Chi_square
- Collective_strength
- Complement_class_support
- Conditional_entropy
- Confidence
- Confidence_causal
- Confirm_causal
- Confirm_descriptive
- Confirmed_confidence_causal
- Correlation_coefficient
- Cosine
- Coverage
- Dir
- F_measure
- Gini_index
- Goodman_kruskal
- Implication_index
- J_measure
- Kappa
- Klosgen
- K-measure
- Kulczynski 2
- Least_contradiction
- Leverage
- Lift
- Loevinger
- Logical_necessity
- Mutual_information
- Normalized_mutual_information
- Odd_multiplier
- Odds_ratio
- One_way_support
- Piatetsky Shapiro
- Prevalence
- Putative_causal_dependency
- Recall
- Relative_risk
- Specificity
- Support
- Theil Uncertainty Coefficiente
- Tic
- Two_way_support
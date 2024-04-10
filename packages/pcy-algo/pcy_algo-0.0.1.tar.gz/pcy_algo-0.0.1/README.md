# PCY implementation 

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)                 
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)   

## Example

# test.py
```
from pcy_algo import pcy_algo
num_transactions = pd.read_csv("path/to/dataset")
hash_func_size = 40 
support = 500 # 5 percentage
confidence = 30
```
# num_transactions containes baskets with items encoded as integers
- num_transactions = [[12,1,2,3,4],[2,3,49,45,12],[12,98,45,22]]
# unique_items contains distinct elements.
- unique_items = (12,1,2,3,4,49,45,98,22)
# create object
```
basket = pcy_algo(num_transactions,unique_items,hash_func_size,support,confidence)
result = basket.mine_data()
```



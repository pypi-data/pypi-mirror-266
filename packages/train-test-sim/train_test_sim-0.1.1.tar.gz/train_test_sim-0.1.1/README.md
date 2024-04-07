[English](README.md) | [Español](./docs/README.es.md) | [Français](./docs/README.fr.md) | [Deutsch](./docs/README.de.md) | [中文](./docs/README.zh.md) | [Türkçe](./docs/README.tr.md) | [日本語](./docs/README.ja.md) | [한국어](./docs/README.ko.md)

## train_test_sim

A library to create quick simulation of optimal train-test size you can keep

Developed by Marcel Tino (c) 2024

## Examples of How To Use the library 

You can use this to alter according to your requirements


```
##syntax
from train_test_sim import get_simulation
model=RandomForestClassifier()
get_simulation(X,Y,model)

you can use any model on sklearn or xgboost. All you need to do is specify correct model name
```


```python
from train_test_sim import get_simulation
from sklearn.datasets import load_diabetes
import numpy as np
from sklearn.ensemble import RandomForestClassifier
diabetes = load_diabetes()
X, y = diabetes.data, diabetes.target

# Convert the target variable to binary (1 for diabetes, 0 for no diabetes)
Y = (y > np.median(y)).astype(int)
model = RandomForestClassifier()

get_simulation(X, Y, model)

```

Note: We can create this for any model


+ Share retail_dictionary on these social media platforms if you like it!
[![Reddit](https://img.shields.io/badge/share%20on-reddit-red?style=flat-square&logo=reddit)](https://reddit.com/submit?url=https://github.com/Kanaries/pygwalker&title=Say%20Hello%20to%20pygwalker%3A%20Combining%20Jupyter%20Notebook%20with%20a%20Tableau-like%20UI)
[![HackerNews](https://img.shields.io/badge/share%20on-hacker%20news-orange?style=flat-square&logo=ycombinator)](https://news.ycombinator.com/submitlink?u=https://github.com/Kanaries/pygwalker)
[![Twitter](https://img.shields.io/badge/share%20on-twitter-03A9F4?style=flat-square&logo=twitter)](https://twitter.com/share?url=https://github.com/Kanaries/pygwalker&text=Say%20Hello%20to%20pygwalker%3A%20Combining%20Jupyter%20Notebook%20with%20a%20Tableau-alternative%20UI)
[![Facebook](https://img.shields.io/badge/share%20on-facebook-1976D2?style=flat-square&logo=facebook)](https://www.facebook.com/sharer/sharer.php?u=https://github.com/Kanaries/pygwalker)
[![LinkedIn](https://img.shields.io/badge/share%20on-linkedin-3949AB?style=flat-square&logo=linkedin)](https://www.linkedin.com/shareArticle?url=https://github.com/Kanaries/pygwalker&&title=Say%20Hello%20to%20pygwalker%3A%20Combining%20Jupyter%20Notebook%20with%20a%20Tableau-alternative%20UI)

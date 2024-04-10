[![Generic badge](https://img.shields.io/badge/Licence-MIT-blue.svg)](https://shields.io/)
[![Generic badge](https://img.shields.io/badge/Maintained-yes-green.svg)](https://shields.io/)
[![Generic badge](https://img.shields.io/badge/Python-3.10-yellow.svg)](https://shields.io/)
[![Generic badge](https://img.shields.io/badge/google_trendy-1.3-red.svg)](https://pypi.org/project/google-trendy/)
[![Build](https://github.com/michaelMondoro/google_trendy/actions/workflows/python-package.yml/badge.svg)](https://github.com/michaelMondoro/google_trendy/actions/workflows/python-package.yml)

## Package
Package for getting and analyzing tending Google searches

## Usage
```python
from google_trendy import *

tracker = GoogleTrends()
tracker.get_trends(10)
for trend in tracker.trends:
    print("----")
    print(f"{trend.title}")
    print(f"{trend.time_range}") 
    print(f"articles: {trend.timeseries_data['article_count']}")


# Example Output
----
Snow emergency, Norfolk, Winter storm, Nebraska, Winter storm warning
Jan 6, 2024 - Now
articles: 18
----
FC Barcelona, CA Osasuna, Raphinha, Supercopa de España, Xavi
Jan 10, 2024 - Now
articles: 4
----
FC Barcelona, Robert Lewandowski, Xavi, LaLiga, Supercopa de España, CA Osasuna, Forward, FC Bayern Munich
Jan 5, 2024 - Now
articles: 6
----
FC Barcelona, Saudi Arabia, Supercopa de España, Spain, LGBT, CA Osasuna, LaLiga
Jan 7, 2024 - Now
articles: 36
----
FC Barcelona, Supercopa de España, CA Osasuna, LaLiga, Xavi, Real Madrid CF, Spain, Copa del Rey
Jan 4, 2024 - Now
articles: 332
----
Supercopa de España, UEFA Super Cup, LaLiga, FC Barcelona, CA Osasuna
Jan 10, 2024 - Now
articles: 3
----
Brooklyn Nets, Cleveland Cavaliers, NBA
Jan 4, 2024 - Now
articles: 325
----
San Antonio Spurs, NBA, Paris, Cleveland Cavaliers, Brooklyn Nets
Jan 8, 2024 - Now
articles: 28
----
Juventus F.C., Coppa Italia, Frosinone Calcio, Serie A, Federico Chiesa
Jan 4, 2024 - Now
articles: 63
----
Spencer Dinwiddie, Brooklyn Nets, Cleveland Cavaliers
Jan 10, 2024 - Now
articles: 5

```

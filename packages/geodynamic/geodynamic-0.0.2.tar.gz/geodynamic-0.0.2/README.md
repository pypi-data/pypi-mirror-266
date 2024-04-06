# GeoDynamic

## Installation

```
pip install --upgrade geodynamic
```

## Using

```
from geodynamic.manim_dynamic import *

class Test(GeoDynamic):
    def construct(self):       
        self.loadGeoGebra('./test.ggb')    
        self.exportSVG('./test_ggb.svg')
```

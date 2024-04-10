# GeoDynamic

## Installation

```bash
pip install --upgrade geodynamic
```

## Using

1. Preparing code `test.py`:

```python
from geodynamic.manim_dynamic import *

class TestScene(GeoDynamic):
    def construct(self):       
        self.loadGeoGebra('test.ggb', scheme = 'pandora', px_size = [400, 300])    
        self.exportSVG('test_ggb.svg')
```

2. Run compilation:

```bash
manim 'test.py' TestScene
```

# remove when black#5214 is closed by PR https://github.com/psf/black/pull/5215
# python run_black.py tests/test_registry_config.py --verbose --diff --target-version=py310
import sys

from blib2to3.pytree import Leaf

# Patch first
if not hasattr(Leaf, "_original_init"):
    Leaf._original_init = Leaf.__init__

    def patched_init(self, *args, **kwargs):
        Leaf._original_init(self, *args, **kwargs)
        self.bracket_depth = 0
        self.opening_bracket = None

    Leaf.__init__ = patched_init

# Import and run Black
from black import patched_main

sys.argv[0] = "black"
sys.exit(patched_main())

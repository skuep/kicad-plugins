# pcbnew loads this folder as a package using import
# thus __init__.py (this file) is executed
# We import the plugin class here and register it to pcbnew
from .action_via_fence_generator import ActionViaFenceGenerator
ActionViaFenceGenerator().register()




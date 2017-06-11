# pcbnew loads this folder as a package using import
# thus __init__.py (this file) is executed
# We import the plugin class here and register it to pcbnew

try:
    from .viafence_action import ViaFenceAction
    ViaFenceAction().register()
except ImportError:
    print('pcbnew package not available. Not registering as a plugin.')
    # pcbnew is not available
    # Thus the package cannot be used as plugin
    pass




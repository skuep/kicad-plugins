# action_viafence
See [Example image](https://github.com/skuep/kicad-plugins/blob/master/action_viafence/tests/simple-test.png).

A via fencing plugin used to place fences of vias next to paths.
Copy the folder into ~/kicad_plugins/ or create a symlink to the the action_viafence folder.

The following libraries are required: pyclipper, wxPython, matplotlib and numpy (temporarily for visualization)

You can access the plugin via pcbnew->Tools->External Plugins->Via Fence Generator. 
It opens a dialog that lets you choose some options and where to get the input tracks from (nets, drawing lines)
However it does not add vias to your board but instead show them in a pyplot window.

You can also run the plugin standalone by cd'ing into the parent folder (i.e. ~/kicad_plugins/) and run

    $ python -m action_viafence --help # Show help 
    $ python -m action_viafence --verbose --test simple-test # starts the simple-test testcase and shows it on the screen
    $ python -m action_viafence --runtests # runs all test cases in the `tests` subdirectory

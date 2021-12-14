# Harness Tools
Harness Tools is a Blender addon for creating and managing cables in designs. It also provides a way to visualize any cable segments that violate minimum bend radius requirements - ideal for routing coaxial cables.

![](docs/MinCurvatureDemo.gif)

# Installation
 - Download the *.zip* file from the [latest release](https://github.com/PhilBladen/BlenderHarnessTools/releases/latest).
 - From Blender, go to *Preferences > Add-ons*, click the *Install...* button and select the downloaded *.zip* file.

# How To Use
 - Select a Bezier curve to become a cable.
 - Go to the harness tools panel (*Preferences > Data > Harness Tools*) and click **Make cable**.
 - Adjust the cable diameter and minimum bend radius using the relevant controls.
 - Enable minimum bend checking by setting **Curvature check** to **Enable**.

![](docs/HowToUse.gif)

# Contribution
If you would like to modify and extend this code, a recommended development environment is Visual Studio Code with the [Blender Development](https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development) extension by Jacques Lucke.

In order to properly resolve the *bpy* Python dependencies, it is recommended to install the latest [fake-bpy-module](https://github.com/nutti/fake-bpy-module) (for this to properly work, the Python interpreter used in VSCode must be the same one that fake-bpy-module is installed to).

# FAQ
**Question:** Why can't I scale my cable?

**Answer:** When a curve is converted to a cable, the object scale is automatically applied locked in order to ensure the cable diameter is accurately displayed. Scaling the locations of the cable points can be done in edit mode instead.

If you need to scale the cable in Object Mode, go to the object's properties and disable the lock next to the scale parameter.

# Changelog
## v0.1.1
 - Updated for full support of Blender 3.0.
 - Fixed warning message due to missing RNA for *test_ot_selectcurves*.
 - Improved code readability.
 - Switched from using *blender_autocomplete* to *fake-bpy-module*.

## v0.1.0
First working release of the Harness Tools plugin:
- Cable creation working.
- Cable diameter and minimum curve radius controls working.
- Visualization of cable areas exceeding minimum bend radius requirements working.
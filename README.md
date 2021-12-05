# Harness Tools
Harness Tools is a Blender addon for creating and managing cables in designs. It also provides a way to visualize any cable segments that violate minimum bend radius requirements - ideal for routing coaxial cables.

# Installation
Download the [latest release](),

# Contribution
Python autocomplete set up using: https://b3d.interplanety.org/en/another-way-to-add-code-autocomplete-when-developing-blender-add-ons-in-visual-studio-code/

# FAQ
**Question:** Why can't I scale my cable?

**Answer:** When a curve is converted to a cable, scaling in Object Mode is automatically locked to ensure the cable diameter is always accurate. It is recommended to scale the cable in edit mode instead.

If you need to scale the cable in Object Mode, go to the object's properties and disable the lock next to the scale parameter.
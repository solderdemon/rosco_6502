# Board preview assets

The main README uses `rosco_6502-board-3d.png`, an orthographic view rendered with OpenGL rasterization. It uses smooth surface normals, linear-light shading and soft rasterized highlights, with no ray tracing or shadow passes. The earlier bare-board top view is retained as `rosco_6502-board.png`.

## 3D models

The PCB references the KiCad 10 standard STEP library through `KICAD10_3DMODEL_DIR`. Install that library to resolve the models. DIP devices include socket models and IC bodies raised 3.5 mm above their normal mounting position. The 100 nF capacitors use compact 3.8 mm ceramic disc models with 2.5 mm lead pitch. C13/C14 retain their 5 mm ceramic disc models; S1 uses the Omron B3F-100x model.

The local [PLCC-44 model](../kicad/3dmodels/PLCC-44_socket_populated.wrl) illustrates the populated UART socket. Its geometry is approximate and is not a manufacturer model of the SCN68681C1A44 or a mechanical clearance specification. Its matching [box definitions](../kicad/3dmodels/PLCC-44_socket_populated.json) replace the converted PLCC geometry in the preview renderer to preserve its colours. The converted and local versions must not be drawn together, because overlapping surfaces cause artifacts. Local model coordinates are in millimetres in the JSON and converted to KiCad VRML units in the WRL.

The render preserves the board thickness and component placements in the PCB file. The preview uses charcoal sleeves for the stock blue electrolytic models. These are presentation colours; exact purchased part numbers were not specified. Generic models do not reproduce device markings or guarantee the dimensions and colours of the purchased components.

## Reproduce the image

Use KiCad 10 with its standard 3D library, Python, `numpy`, `trimesh`, `moderngl` and `Pillow`, and an OpenGL 3.3 capable graphics driver. Run from the repository root, with `kicad-cli` on PATH:

```sh
kicad-cli pcb export glb --output rosco-populated.glb --force --include-pads --include-silkscreen --include-soldermask design/kicad/rosco_6502.kicad_pcb
python design/assets/render_board.py rosco-populated.glb design/assets/rosco_6502-board-3d.png
```

The GLB is an intermediate file and does not need to be committed. The renderer adds the local UART visualization at the current IC3 position; update that placement in the script if IC3 is moved. It uses an orthographic camera and renders at twice the output resolution before downsampling to 1800 × 1400 pixels.

The local illustrative PLCC model is covered by the project's [hardware licence](../../LICENCE.hardware.txt). Standard KiCad models retain their upstream licences and are referenced rather than copied into this repository.

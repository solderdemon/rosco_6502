"""Render a KiCad GLB with OpenGL rasterization and an orthographic camera.

Usage: python design/assets/render_board.py input.glb output.png
Requires numpy, trimesh, moderngl and Pillow. No ray tracing or shadow passes.
"""
from pathlib import Path
import argparse
import json
import numpy as np
import moderngl
import trimesh
from PIL import Image

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('input', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
scene = trimesh.load_scene(args.input)

# Replace the GLB's converted PLCC geometry with the local coloured model.
# Do not draw both versions: their overlapping surfaces cause z-fighting.
boxes_path = Path(__file__).resolve().parents[1] / 'kicad/3dmodels/PLCC-44_socket_populated.json'
for box in json.loads(boxes_path.read_text()):
    x, y, z = box['center']
    sx, sy, sz = box['size']
    mesh = trimesh.creation.box(extents=np.array([sx, sz, sy]) / 1000)
    mesh.apply_translation([(103.27+x)/1000, (4.6+z)/1000, (121.65-y)/1000])
    mesh.visual.vertex_colors = (np.array([*box['color'], 1.0]) * 255).astype(np.uint8)
    scene.add_geometry(mesh)

positions, normals, colors = [], [], []
for node in scene.graph.nodes_geometry:
    transform, name = scene.graph[node]
    if name.startswith('PLCC-44_socket_populated'):
        continue
    mesh = scene.geometry[name]
    faces = mesh.faces
    vertices = trimesh.transform_points(mesh.vertices, transform)
    # Area-weighted normals need only NumPy, not optional SciPy.
    normal = np.zeros_like(mesh.vertices)
    triangle = mesh.vertices[faces]
    cross = np.cross(triangle[:, 1]-triangle[:, 0], triangle[:, 2]-triangle[:, 0])
    for corner in range(3):
        np.add.at(normal, faces[:, corner], cross)
    normal = normal @ np.linalg.inv(transform[:3, :3])
    normal /= np.maximum(np.linalg.norm(normal, axis=1, keepdims=True), 1e-12)
    positions.append(vertices[faces].reshape(-1, 3))
    if mesh.visual.kind == 'texture':
        normals.append(normal[faces].reshape(-1, 3))
    else:
        face_normal = mesh.face_normals @ np.linalg.inv(transform[:3, :3])
        normals.append(np.repeat(face_normal, 3, axis=0))
    if mesh.visual.kind == 'texture':
        color = mesh.visual.material.baseColorFactor[:3] / 255.0
    else:
        color = mesh.visual.vertex_colors[0, :3] / 255.0
    alpha = 1.0
    # Match the bright KiCad preview palette used by the busboard reference.
    if name.startswith('rosco_6502_PCB'):
        if np.allclose(color, np.array([20,51,36])/255, atol=0.005):
            color = np.array([0.14,0.25,0.17])
            alpha = 0.32  # let copper tracks remain visible through soldermask
        elif np.allclose(color, np.array([107,115,74])/255, atol=0.005):
            color = np.array([0.34,0.36,0.27])
        elif np.allclose(color, np.array([128,128,128])/255, atol=0.005):
            color = np.array([1.0,0.88,0.05])
    if 'C_Disc' in name and color[0] > color[1]*2:
        color = np.array([0.78,0.36,0.08])
    if np.allclose(color, np.array([4,34,124])/255, atol=0.005):
        color = np.array([0.12,0.43,0.88])
    if 'R_Axial' in name and color[0] > color[2]*1.5:
        color = np.array([0.88,0.74,0.49])
    color = np.maximum(color, 0.09)
    colors.append(np.tile([*color,alpha], (len(faces)*3, 1)))

vertices = np.concatenate(positions)
center = (vertices.min(axis=0) + vertices.max(axis=0)) / 2
# Looking down from the front-left; the board's top edge stays at the back.
back = np.array([-0.62, 1.65, 1.0]); back /= np.linalg.norm(back)
right = np.cross([0, 1, 0], back); right /= np.linalg.norm(right)
up = np.cross(back, right)
rotation = np.array([right, up, back])
view_vertices = (vertices-center) @ rotation.T
view_normals = np.concatenate(normals) @ rotation.T
width, height, supersampling = 2400, 1800, 2
extent = np.ptp(view_vertices[:, :2], axis=0)
view_height = max(extent[1], extent[0] * height/width) * 1.12
view_width = view_height * width/height
midpoint = (view_vertices[:, :2].min(axis=0) + view_vertices[:, :2].max(axis=0))/2
view_vertices[:, :2] -= midpoint
view_vertices[:, 0] *= 2/view_width
view_vertices[:, 1] *= 2/view_height
view_vertices[:, 2] *= -2 / (np.ptp(view_vertices[:, 2]) * 1.2)
data = np.column_stack([view_vertices, view_normals, np.concatenate(colors)]).astype('f4')
ctx = moderngl.create_standalone_context()
ctx.enable(moderngl.DEPTH_TEST)
program = ctx.program(vertex_shader='''#version 330
in vec3 position; in vec3 normal; in vec4 color;
out vec3 n; out vec4 c;
void main() { gl_Position=vec4(position,1.0); n=normal; c=color; }
''', fragment_shader='''#version 330
in vec3 n; in vec4 c; out vec4 result;
void main() {
 vec3 normal=normalize(n);
 if(!gl_FrontFacing) normal=-normal;
 vec3 key=normalize(vec3(-0.6,0.9,1.0));
 vec3 fill=normalize(vec3(0.9,0.2,0.7));
 float light=0.60+0.40*max(dot(normal,key),0.0)+0.15*max(dot(normal,fill),0.0);
 vec3 halfway=normalize(key+vec3(0.0,0.0,1.0));
 float spec=0.025*pow(max(dot(normal,halfway),0.0),32.0);
 // Shade in linear light, then encode sRGB for the PNG.
 vec3 linear=pow(c.rgb,vec3(2.2))*light+vec3(spec);
 result=vec4(pow(linear,vec3(1.0/2.2)),c.a);
}
''')
frame = ctx.simple_framebuffer((width*supersampling, height*supersampling), components=4)
frame.use(); frame.clear(0.0,0.0,0.0,0.0,depth=1.0)
triangles = data.reshape(-1,3,10)
opaque = triangles[:,0,9] >= 0.999
for transparent in (False,True):
    batch = triangles[~opaque if transparent else opaque]
    if transparent:
        # Back-to-front compositing after the opaque depth pass.
        batch = batch[np.argsort(-batch[:,:,2].mean(axis=1))]
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = (moderngl.SRC_ALPHA,moderngl.ONE_MINUS_SRC_ALPHA,moderngl.ONE,moderngl.ONE_MINUS_SRC_ALPHA)
        ctx.depth_mask = False
    if len(batch):
        vao=ctx.vertex_array(program,[(ctx.buffer(batch.tobytes()),'3f 3f 4f','position','normal','color')])
        vao.render(moderngl.TRIANGLES)

image=Image.frombytes('RGBA',frame.size,frame.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
image=image.resize((width,height),Image.Resampling.LANCZOS)
image.save(args.output)
print(f'Rendered {len(data)//3:,} triangles using {ctx.info["GL_RENDERER"]}: {args.output}')

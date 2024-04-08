# En __init__.py del paquete que contiene AtomPositionManager
try:
    from sage_lib.partition.PartitionManager import PartitionManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing PartitionManager: {str(e)}\n")
    del syss

try:
    from sage_lib.IO.structure_handling_tools.AtomPosition import AtomPosition
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing AtomPosition: {str(e)}\n")
    del sys
    
try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:
    import subprocess
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing subprocess: {str(e)}\n")
    del sys

try:
    import copy
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing copy: {str(e)}\n")
    del sys

class Blender_builder(PartitionManager):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        """
        Constructor method for initializing the beldenr  instance.
        """
        super().__init__(name=name, file_location=file_location)

    def get_blender_str(self, atomPositions, atomLabelsList, uniqueAtomLabels, latticeVectors,
                            atomCount, colors, radii, conection, fog, path,
                            scale, camera,
                            samples, resolution_x, resolution_y, ):
        '''
        atomPositions = { atomPositions }
        atomLabelsList = { atomLabelsList }
        uniqueAtomLabels = {uniqueAtomLabels}
        atomCount = { atomCount }
        colors = { colors }
        radii = { radii }
        conection = {conection}
        '''
        atomPositions = np.array(atomPositions) # - np.min(atomPositions,axis=0) - np.ptp(atomPositions,axis=0)/2
        atomLabelsList = np.array(atomLabelsList)
        uniqueAtomLabels = np.array(uniqueAtomLabels)
        latticeVectors = np.array(latticeVectors)

        camera_X, camera_Y, camera_Z = 'x' in camera, 'y' in camera, 'z' in camera

        self.blender_script = f"""
import bpy
import random
from mathutils import Vector
import numpy as np

def create_object_instance(original, location=(0,0,0), rotation=(0,0,0), scale=(1,1,1)):
    # Create a new linked duplicate (instance) of the original object
    instance = bpy.data.objects.new(name=original.name + "_instance", object_data=original.data)
    instance.location = location
    instance.rotation_euler = rotation
    instance.scale = scale
    bpy.context.collection.objects.link(instance)

    return instance

def align_object_between_points(obj, start_point, end_point):
    # Calculate the direction vector from start to end point
    direction = end_point - start_point
    # Calculate the midpoint
    midpoint = start_point + direction / 2
    obj.location = midpoint
    # Calculate the rotation to align with the direction vector
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = direction.to_track_quat('Z', 'Y')
    # Scale the object to stretch between the two points
    obj.scale[2] = direction.length / 2 # Assuming the cylinder's length aligns with the Z-axis

def setup_scene():
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    sphere_original = {{}}
    cylinder_original = {{}}
    for label in uniqueAtomLabels:
        # Create original sphere and cylinder
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radii[label]*0.88 )
        sphere_original[label] = bpy.context.object
        sphere_original[label].name = f'sphere label{{label}}'
        bpy.ops.object.shade_smooth()

        bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=2)
        cylinder_original[label] = bpy.context.object
        cylinder_original[label].name = f'cylinder label{{label}}'
        bpy.ops.object.shade_smooth()

    # Generate sphere instances at random positions
    for i, n in enumerate(atomPositions): # Number of spheres
        loc = (n[0], n[1], n[2])
        sphere_instance = create_object_instance(sphere_original[atomLabelsList[i]], location=loc)

    # Connect sphere instances with cylinder instances
    for [A, B] in conection:
        cylinder_instance_A = create_object_instance( cylinder_original[atomLabelsList[A]] )
        cylinder_instance_B = create_object_instance( cylinder_original[atomLabelsList[B]] )
        
        midpoint = Vector((np.array(atomPositions[A]) + np.array(atomPositions[B]))/2)
        
        align_object_between_points(cylinder_instance_A, Vector(atomPositions[A]), midpoint )
        align_object_between_points(cylinder_instance_B, midpoint, Vector(atomPositions[B]) )

    return sphere_original, cylinder_original

def create_material(name,  base_color, metallic=0.7, specular=0.9, roughness=0.5 ):
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = base_color + (1,)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Specular'].default_value = specular
    bsdf.inputs['Roughness'].default_value = roughness

    return material

def setup_lighting():
    # Remove existing lights
    bpy.ops.object.select_by_type(type='LIGHT')
    bpy.ops.object.delete()
    
    # Key light
    #bpy.ops.object.light_add(type='AREA', radius=5, location=(0, 10, 10))
    #bpy.context.object.data.energy = 1000

    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    sun = bpy.context.object
    sun.data.energy = 5 # Adjust as needed
    sun.data.angle = np.radians(15) 

    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    sun = bpy.context.object
    sun.data.energy = 5 # Adjust as needed
    sun.data.angle = np.radians(165) 


    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    sun = bpy.context.object
    sun.data.energy = 5 # Adjust as needed
    sun.data.angle = np.radians(90) 

def setup_background(color=(0.05, 0.05, 0.05, 1)):
    # Set the background color
    bpy.context.scene.world.use_nodes = True
    bg = bpy.context.scene.world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = color
    bpy.context.scene.render.film_transparent = True

def add_camera(name, location, look_at_point, ortho_scale, scale:str='orthographic'):
    # Create the camera
    bpy.ops.object.camera_add(location=Vector(location) ) 
    camera = bpy.context.object
    camera.name = name
    
    if scale == 'orthographic':
        camera.data.type = 'ORTHO'
        camera.data.ortho_scale = ortho_scale  # Controls the size of the orthographic view
    
    # Point the camera to the look_at_point
    direction = Vector(look_at_point) - Vector(location)
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()

def setup_cameras(look_at_point):
    distance = 20 # Distance from the center to place cameras
    add_camera('Camera_X', (distance, 0, 0), look_at_point)
    add_camera('Camera_Y', (0, distance, 0), look_at_point)
    add_camera('Camera_Z', (0, 0, distance), look_at_point)

def setup_orthographic_cameras(lattice_vectors, look_at_point):
    # Calcula las esquinas de la celda unidad
    corners = [np.dot(np.array([x, y, z]), lattice_vectors) for x in (0, 1) for y in (0, 1) for z in (0, 1)]
    
    # Determina el centro de la vista y la distancia para ubicar las cámaras
    center = look_at_point # np.mean(corners, axis=0)
    distance = np.max(np.ptp(corners, axis=0)) * 2.5  # Max peak-to-peak distance as a simple factor
    
    # Escalas ortográficas para cada eje, ajustadas según el ancho y alto de los ejes restantes
    ortho_scales = {{
        'x': np.max([np.ptp(corners, axis=0)[1], np.ptp(corners, axis=0)[2]]) * 1.05 * {scale},  # Y-Z plane
        'y': np.max([np.ptp(corners, axis=0)[0], np.ptp(corners, axis=0)[2]]) * 1.05 * {scale},  # X-Z plane
        'z': np.max([np.ptp(corners, axis=0)[0], np.ptp(corners, axis=0)[1]]) * 1.05 * {scale},  # X-Y plane
    }}

    camera_positions = {{ }}

    if {camera_X}:
        camera_positions['Camera_X'] = (center[0] + distance, center[1], center[2])
    if {camera_Y}:
        camera_positions['Camera_Y'] = (center[0], center[1] + distance, center[2])
    if {camera_Z}:
        camera_positions['Camera_Z'] = (center[0], center[1], center[2] + distance)

    # Añade cada cámara con su respectiva configuración
    for camera, pos in camera_positions.items():
        axis = camera[-1].lower()  # Extrae el eje (x, y, z) de la etiqueta de la cámara
        ortho_scale = ortho_scales[axis]
        add_camera(camera, pos, center, ortho_scale, scale='orthographic')

def find_molecular_centroid():
    # Find the centroid of all sphere instances (assuming they represent atoms)
    return lattice_vectors

def find_unit_cell_center(lattice_vectors):
    return np.sum( np.array(lattice_vectors), axis=0) / 2

def setup_compositing_nodes():
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    # Clear default nodes
    for node in tree.nodes:
        tree.nodes.remove(node)
    
    # Create nodes for post-processing effects
    render_layers = tree.nodes.new('CompositorNodeRLayers')
    viewer = tree.nodes.new('CompositorNodeViewer') # To view the effect directly in Blender
    comp = tree.nodes.new('CompositorNodeComposite') # To ensure output is rendered

    # Example of adding a glare effect
    glare = tree.nodes.new('CompositorNodeGlare')
    glare.glare_type = 'FOG_GLOW' # Experiment with different types like 'FOG_GLOW', 'SIMPLE_STAR', etc.
    glare.mix = 0.1 # Blend with the original image
    glare.threshold = 0.8 # Intensity threshold for the glare effect
    
    # Connect the nodes
    tree.links.new(render_layers.outputs[0], glare.inputs[0]) # Connect Render Layers to Glare
    tree.links.new(glare.outputs[0], viewer.inputs[0]) # Connect Glare to Viewer
    tree.links.new(glare.outputs[0], comp.inputs[0]) # Ensure the output is connected to Composite for rendering

    # Add more effects as needed (e.g., color correction, depth of field, vignette)


def high_quality_render_settings(engine:str='CYCLES', samples:int={samples}, resolution_x:int={resolution_x}, resolution_y:int={resolution_y}, use_denoising:bool=True):
    bpy.context.scene.render.engine = str(engine) # Use Cycles for better quality
    # Obtener las preferencias de Blender
    prefs = bpy.context.preferences
    # Acceder a las configuraciones de Cycles
    cycles_prefs = prefs.addons['cycles'].preferences

    # Establecer el dispositivo de renderizado a 'GPU'
    cycles_prefs.compute_device_type = 'CUDA' # O 'OPENCL' dependiendo de tu hardware

    # Activar todos los dispositivos GPU disponibles
    for device in cycles_prefs.devices:
        if device.type == 'CUDA':  # O 'OPENCL' dependiendo de tu configuración
            device.use = True

    # Configurar la escena para usar GPU
    bpy.context.scene.cycles.device = 'GPU'

    bpy.context.scene.cycles.samples = samples # Increase for higher quality but longer render times
    bpy.context.scene.render.resolution_x = resolution_x # Increase resolution
    bpy.context.scene.render.resolution_y = resolution_y

    if use_denoising:
        bpy.context.scene.cycles.use_denoising = True # Enable denoising
        
        # Enable denoising
        bpy.context.scene.cycles.use_denoising = True
        
        # Advanced denoising settings for finer control
        bpy.context.scene.cycles.denoising_store_passes = True
        #bpy.context.scene.view_layers["View Layer"].cycles.use_denoising = True
        
        # Opt-in for AI-accelerated denoiser (requires NVIDIA OptiX)
        bpy.context.scene.cycles.denoiser = 'OPTIX'  # Alternatives: 'NLM', 'OPENIMAGEDENOISE'
    
        # Set denoising after rendering for more control
        #bpy.context.scene.view_layers["View Layer"].cycles.denoising_prefilter = 'ACCURATE'
        #bpy.context.scene.view_layers["View Layer"].cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
        
        # Adjust as per the complexity of the scene; for detailed models, consider increasing samples further.
        #bpy.context.scene.cycles.preview_samples = 10  # Samples for viewport preview
        
        # Enable Adaptive Sampling for efficiency
        #bpy.context.scene.cycles.use_adaptive_sampling = True
        #bpy.context.scene.cycles.adaptive_threshold = 0.01  # Lower threshold for higher quality

def add_fog():
    # Crea un objeto de volumen para la neblina
    bpy.ops.mesh.primitive_cube_add(size=20, location=(0, 0, 0))  # Ajusta el tamaño según sea necesario
    cube = bpy.context.object
    cube.name = 'FogVolume'

    # Crea un nuevo material volumétrico
    mat_fog = bpy.data.materials.new(name="FogMaterial")
    cube.data.materials.append(mat_fog)
    mat_fog.use_nodes = True
    nodes = mat_fog.node_tree.nodes

    # Limpia los nodos predeterminados
    for node in nodes:
        nodes.remove(node)

    # Añade un nodo de Principled Volume
    volume_shader = nodes.new(type='ShaderNodeVolumePrincipled')
    volume_shader.location = 0, 0

    # Añade un nodo de salida de material
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = 200, 0

    # Añade un nodo de textura de ruido para variar la densidad de la neblina
    noise_tex = nodes.new(type='ShaderNodeTexNoise')
    noise_tex.location = -200, 0
    noise_tex.inputs['Scale'].default_value = 5.0  # Ajusta para más o menos detalle en la neblina

    # Conecta los nodos
    links = mat_fog.node_tree.links
    links.new(noise_tex.outputs['Fac'], volume_shader.inputs['Density'])
    links.new(volume_shader.outputs['Volume'], output_node.inputs['Volume'])

    # Ajusta la densidad de la neblina (baja para empezar, aumenta según sea necesario)
    volume_shader.inputs['Density'].default_value = 0.01

    # Añade un nodo Math para ajustar la influencia de la textura de ruido en la densidad
    math_node = nodes.new(type='ShaderNodeMath')
    math_node.operation = 'MULTIPLY'
    math_node.inputs[1].default_value = 0.08  # Ajusta este valor para controlar la densidad general
    math_node.location = -400, 0

    # Conecta el nodo de ruido al nodo Math y luego al shader de volumen
    links.new(noise_tex.outputs['Fac'], math_node.inputs[0])
    links.new(math_node.outputs[0], volume_shader.inputs['Density'])

def draw_lattice_edges_with_material(lattice_vectors, edge_radius=0.01, edge_color=(0.5, 0.5, 0.5, 1)):

    # Función para crear material
    def create_edge_material(name, color):
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        bsdf = material.node_tree.nodes.get('Principled BSDF')
        bsdf.inputs['Base Color'].default_value = color
        return material

    # Crear material para las aristas
    edge_material = create_edge_material("EdgeMaterial", edge_color)

    # Calcula las posiciones de las esquinas de la celda unitaria
    corners = [np.dot(np.array([x, y, z]), lattice_vectors) for x in (0, 1) for y in (0, 1) for z in (0, 1)]

    # Define los pares de esquinas que forman cada arista de la celda
    edges = [(0, 1), (1, 3), (3, 2), (2, 0), 
             (4, 5), (5, 7), (7, 6), (6, 4),
             (0, 4), (1, 5), (2, 6), (3, 7)]
    
    # Dibuja cada arista como un cilindro entre dos esquinas
    for start, end in edges:
        start_point = corners[start]
        end_point = corners[end]
        midpoint = (np.array(start_point) + np.array(end_point)) / 2
        length = np.linalg.norm(np.array(start_point) - np.array(end_point))
        
        bpy.ops.mesh.primitive_cylinder_add(radius=edge_radius, depth=length, location=midpoint)
        cylinder = bpy.context.object

        # Orienta el cilindro correctamente
        direction = np.array(end_point) - np.array(start_point)
        rot_axis = np.cross([0, 0, 1], direction)
        if np.linalg.norm(rot_axis) != 0:
            rot_angle = np.arccos(np.dot([0, 0, 1], direction) / np.linalg.norm(direction))
            cylinder.rotation_mode = 'AXIS_ANGLE'
            cylinder.rotation_axis_angle = [rot_angle] + list(rot_axis)
        else:
            # Si la dirección ya es [0, 0, 1] o [0, 0, -1], no se requiere rotación
            if np.allclose(direction, [0, 0, -1]):
                cylinder.rotation_euler = [np.pi, 0, 0]

        # Asigna el material a las aristas
        if not cylinder.data.materials:
            cylinder.data.materials.append(edge_material)
        else:
            cylinder.data.materials[0] = edge_material

atomPositions = { np.array(atomPositions).tolist() }
atomLabelsList = { np.array(atomLabelsList).tolist() }
uniqueAtomLabels = { np.array(uniqueAtomLabels).tolist() }
lattice_vectors = { np.array(latticeVectors).tolist() }
atomCount = { atomCount }
colors = { colors }
radii = { radii }
conection = {conection}

sphere_original, cylinder_original = setup_scene()

material_sphere = {{label: create_material('SphereMaterial', colors[label]) for label in uniqueAtomLabels }}# Red
material_cylinder = {{label: create_material('CylinderMaterial', colors[label]) for label in uniqueAtomLabels }}# Blue

for obj in bpy.context.scene.objects:
    for label in uniqueAtomLabels:
        if "sphere" in obj.name.lower() and 'label'+label.lower() in obj.name.lower():
            if obj.data.materials:
                obj.data.materials[0] = material_sphere[label]
            else:
                obj.data.materials.append( material_sphere[label] )
            break
        
        elif "cylinder" in obj.name.lower() and 'label'+label.lower() in obj.name.lower():
            if obj.data.materials:
                obj.data.materials[0] = material_cylinder[label]
            else:
                obj.data.materials.append(material_cylinder[label])
            break


for label in uniqueAtomLabels:
    sphere_original[label].hide_render = True
    sphere_original[label].hide_viewport = True

    cylinder_original[label].hide_render = True
    cylinder_original[label].hide_viewport = True

draw_lattice_edges_with_material(lattice_vectors)

setup_lighting()
setup_background() # rgay by defoault 
setup_orthographic_cameras(lattice_vectors, find_unit_cell_center(lattice_vectors))
setup_compositing_nodes()

high_quality_render_settings()

if {fog}: add_fog()

def render_scene(camera_name, output_path):
    # Set the active camera
    bpy.context.scene.camera = bpy.data.objects[camera_name]

    # Set render settings
    bpy.context.scene.render.image_settings.file_format = 'PNG'  # or any other format
    bpy.context.scene.render.filepath = output_path

    # Render the scene
    bpy.ops.render.render(write_still=True)

# Render and save the image from each camera
cameras = ['Camera_X', 'Camera_Y', 'Camera_Z']
for camera in cameras:
    output_path = f"{path}_{{camera}}.png"  # Update the output path
    render_scene(camera, output_path)

"""
        return self.blender_script

    def handleBLENDER(self, values:list ):
        """
        Handle molecular dynamics analysis based on specified values.

        Args:
            values (list): List of analysis types to perform.
        """

        def _generate_supercell(APM, repeat:np.array=np.array([1,1,1], dtype=np.int64) ):
            """
            Generate a supercell from a given unit cell in a crystalline structure.

            Parameters:
            - repeat (list): A list of three integers (nx, ny, nz) representing the number of times the unit cell is replicated 
                                along the x, y, and z directions, respectively.

            Returns:
            - np.array: An array of atom positions in the supercell.
            """

            # Extract lattice vectors from parameters
            a, b, c = APM.latticeVectors
            nx, ny, nz = repeat

            # Generate displacement vectors
            displacement_vectors = [a * i + b * j + c * k for i in range(-nx, nx+1) for j in range(-ny, ny+1) for k in range(-nz, nz+1)]

            # Replicate atom positions and apply displacements
            atom_positions = np.array(APM.atomPositions)
            supercell_positions = np.vstack([atom_positions + dv for dv in displacement_vectors])

            # Replicate atom identities and movement constraints
            supercell_atomLabelsList = np.tile(APM.atomLabelsList, (nx*2+1) * (ny*2+1) * (nz*2+1))
            supercell_atomicConstraints = np.tile(APM.atomicConstraints, ( (nx*2+1) * (ny*2+1) * (nz*2+1) , 1))

            APM._atomLabelsList = supercell_atomLabelsList
            APM._atomicConstraints = supercell_atomicConstraints
            APM._atomPositions = supercell_positions
            APM._latticeVectors *= np.array(repeat*2+1)[:, np.newaxis]
            APM._atomPositions_fractional = None
            APM._atomCount = None
            APM._atomCountByType = None
            APM._fullAtomLabelString = None

            return APM

        MDA_data = {}

        for plot in values:
            for container_index, container in enumerate(self.containers):
                if plot.upper() == 'RENDER':
                    repeat = np.array(values[plot]['repeat'])
                    container.AtomPositionManager = _generate_supercell(container.AtomPositionManager, repeat=repeat ) 

                    blender_str = self.get_blender_str(
                        atomPositions = container.AtomPositionManager.atomPositions, 
                        atomLabelsList =  container.AtomPositionManager.atomLabelsList, 
                        uniqueAtomLabels =  container.AtomPositionManager.uniqueAtomLabels, 
                        latticeVectors = container.AtomPositionManager.latticeVectors,
                        atomCount =  container.AtomPositionManager.atomCount, 
                        colors = container.AtomPositionManager.element_colors, 
                        radii = container.AtomPositionManager.atomic_radii_empirical, 
                        conection =  container.AtomPositionManager.get_connection_list(sigma=values[plot]['sigma'], periodic=False),
                        fog = values[plot]['fog'], 
                        path = f'blender_plot_{container_index}_',
                        resolution_x = values[plot]['resolution_x'], 
                        resolution_y = values[plot]['resolution_y'], 
                        samples = values[plot]['samples'], 
                        camera = values[plot]['camera'], 
                        scale = values[plot]['scale'], 
                        )
                    
                    blender_script_name = f'blender_script_{container_index}.py'
                    with open(blender_script_name, 'w') as file:
                        file.write(blender_str)

                    if values[plot]['verbose']:
                        print(f'>> Blender script save to {blender_script_name} ')

                    if values[plot]['render']:
                        command = f'blender -b -P {blender_script_name}'
                        process = subprocess.run(command, shell=True, check=True)

                        if values[plot]['verbose']:
                            print(f'>> DONE :: Render container {container_index} finish ')


'''

    distance = { (np.max(atomPositions, axis=0)+7).tolist() }  # Distance from the center to place cameras. Adjust based on model size
    # The ortho_scale might need adjustment depending on the size of your molecular model
    ortho_scale = { [ np.max([np.ptp(atomPositions[:, 1]), np.ptp(atomPositions[:, 2])])*2, np.max([np.ptp(atomPositions[:, 0]), np.ptp(atomPositions[:, 2])])*2, np.max([np.ptp(atomPositions[:, 0]), np.ptp(atomPositions[:, 1])])*2 ] } 

    #corners = [np.dot(np.array([x, y, z]), lattice_vectors) for x in (0, 1) for y in (0, 1) for z in (0, 1)]

    add_camera('Camera_X', (distance[0], 0, 0), look_at_point, ortho_scale[0], scale='orthographic')
    add_camera('Camera_Y', (0, distance[1], 0), look_at_point, ortho_scale[1], scale='orthographic')
    add_camera('Camera_Z', (0, 0, distance[2]), look_at_point, ortho_scale[2], scale='orthographic')
'''
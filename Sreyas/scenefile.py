import json
import pprint
import numpy as np

#TODO: Abstract the logic of scene element into a separate class.
#TODO: Add full list of animable params.
#TODO: Support animation in parallel over multiple params.

mkfiles_path = "gs://sandbox-ce2c5.appspot.com/mkturkfiles"

class Camera:

    def __init__(self, name="cam",
                 camera_type="PerspectiveCamera", 
                 fov=45, near=0.1, far=2000, visible=1):
        self.name = name
        self.camera_type = camera_type
        self.field_of_view = fov
        self.near = near
        self.far = far
        self.num_stimuli = 1
        self.position = [[0]*self.num_stimuli] * 3
        self.target = [[0]*self.num_stimuli] * 3
        self.visible = visible

    def set_position(self, position):
        assert len(position) == 3, "Position must be given as (x, y, z)!"
        assert len(position[0]) == len(position[1]) == len(position[2]), "(x, y, z) stimulus lengths must match!"
        self.position = position
        self.num_stimuli = max(self.num_stimuli, len(position[0]))
    
    def set_target(self, target):
        assert len(target) == 3, "Target must be given as (x, y, z)!"
        assert len(target[0]) == len(target[1]) == len(target[2]), "(x, y, z) stimulus lengths must match!"
        self.target = target
        self.num_stimuli = max(self.num_stimuli, len(target[0]))

    def is_consistent(self):
        return len(self.position[0]) == len(self.target[0]) == self.num_stimuli
    
    def duplicate(self, factor):
        self.set_position([self.position[i]*factor for i in range(3)])
        self.set_target([self.target[i]*factor for i in range(3)])

    def copy(self):
        cam = Camera(self.name, self.camera_type, self.field_of_view,
                     self.near, self.far, self.visible)
        cam.set_position(self.position.copy())
        cam.set_target(self.target.copy())
        return cam

    def subset(self, i, j):
        assert i <= j and i >= 0 and j <= self.num_stimuli, "Improper indices for subset, please try again!"
        sub_cam = Camera(self.name, self.camera_type, self.field_of_view,
                         self.near, self.far, self.visible)
        sub_cam.set_position([self.position[k][i:j+1] for k in range(3)])
        sub_cam.set_target([self.target[k][i:j+1] for k in range(3)])
        return sub_cam

    def concatenate(cam1, cam2):
        assert cam1.is_consistent() and cam2.is_consistent(), "Cameras must be consistent to concatenate!"
        assert cam1.name == cam2.name, "Camera names must match!"
        assert cam1.camera_type == cam2.camera_type, "Camera types must match!"
        assert cam1.field_of_view == cam2.field_of_view, "Camera fovs must match!"
        assert cam1.near == cam2.near, "Camera nears must match!"
        assert cam1.far == cam2.far, "Camera fars must match!"
        assert cam1.visible == cam2.visible, "Camera visibles must match!"
        cam = Camera(cam1.name, cam1.camera_type, 
                     cam1.field_of_view, 
                     cam1.near, cam1.far, 
                     cam1.visible)
        cam.set_position([cam1.position[i] + cam2.position[i] for i in range(3)])
        cam.set_target([cam1.target[i] + cam2.target[i] for i in range(3)])
        return cam

    def to_dict(self):
        cam_dict = {"type": self.camera_type,
                    "fieldOfView": self.field_of_view,
                    "near": self.near,
                    "far": self.far,
                    "position": {"x": self.position[0],
                                 "y": self.position[1],
                                 "z": self.position[2]},
                    "targetTHREEJS": {"x": self.target[0],
                                 "y": self.target[1],
                                 "z": self.target[2]},
                    "visible": [self.visible]}
        return cam_dict
    
    def from_dict(cam_dict, name):
        camera_type = cam_dict["type"]
        field_of_view = cam_dict["fieldOfView"]
        near = cam_dict["near"]
        far = cam_dict["far"]
        if "visible" in cam_dict.keys():
            if isinstance(cam_dict["visible"], int): 
                visible = cam_dict["visible"]
            else: 
                assert len(cam_dict["visible"]) == 1, "Animating camera visible is not yet supported."
                visible = cam_dict["visible"][0]
        else:
            print("Camera visible flag not found. Setting to 1.")
            visible = 1
        pos = [cam_dict["position"]["x"],
               cam_dict["position"]["y"], 
               cam_dict["position"]["z"]]
        tgt = [cam_dict["targetTHREEJS"]["x"],
               cam_dict["targetTHREEJS"]["y"], 
               cam_dict["targetTHREEJS"]["z"]]
        num_pos_stimuli = max([len(pos[i]) for i in range(3)])
        num_tgt_stimuli = max([len(tgt[i]) for i in range(3)])
        num_stimuli = max(num_pos_stimuli, num_tgt_stimuli)
        for i in range(3):
            if len(pos[i]) == 1: pos[i] = pos[i]*num_stimuli
            if len(tgt[i]) == 1: tgt[i] = tgt[i]*num_stimuli
        camera = Camera(name, camera_type,
                        field_of_view,
                        near, far,
                        visible)
        camera.set_position(pos)
        camera.set_target(tgt)
        return camera
    
class Light:

    def __init__(self, name="light", light_type="DirectionalLight", color=0xffffff, intensity=5, visible=1):
        self.name = name
        self.light_type = light_type
        self.color = color
        self.intensity = intensity
        self.visible = visible
        self.num_stimuli = 1
        self.position = [[0]*self.num_stimuli] * 3

    def set_position(self, position):
        assert len(position) == 3, "Position must be given as (x, y, z)!"
        assert len(position[0]) == len(position[1]) == len(position[2]), "(x, y, z) stimulus lengths must match!"
        self.position = position
        self.num_stimuli = max(self.num_stimuli, len(position[0]))

    def is_consistent(self):
        return len(self.position[0]) == self.num_stimuli
    
    def duplicate(self, factor):
        self.set_position([self.position[i]*factor for i in range(3)])

    def copy(self):
        light = Light(self.name, self.light_type, self.color,
                         self.intensity, self.visible)
        light.set_position(self.position.copy())
        return light

    def subset(self, i, j):
        assert i <= j and i >= 0 and j <= self.num_stimuli, "Improper indices for subset, please try again!"
        sub_light = Light(self.name, self.light_type, self.color,
                         self.intensity, self.visible)
        sub_light.set_position([self.position[k][i:j+1] for k in range(3)])
        return sub_light

    def concatenate(light1, light2):
        assert light1.is_consistent() and light2.is_consistent(), "Lights must be consistent to concatenate!"
        assert light1.name == light2.name, "Light names must match!"
        assert light1.light_type == light2.light_type, "Light types must match!"
        assert light1.color == light2.color, "Light colors must match!"
        assert light1.intensity == light2.intensity, "Light intensities must match!"
        assert light1.visible == light2.visible, "Light visibles must match!"
        light = Light(light1.name, light1.light_type,
                     light1.color, 
                     light1.intensity, 
                     light1.visible)
        light.set_position([light1.position[i] + light2.position[i] for i in range(3)])
        return light

    def to_dict(self):
        light_dict = {"type": self.light_type,
                    "color": self.color,
                    "intensity": [self.intensity],
                    "position": {"x": self.position[0],
                                 "y": self.position[1],
                                 "z": self.position[2]},
                    "visible": [self.visible]}
        return light_dict
    
    def from_dict(light_dict, name):
        light_type = light_dict["type"]
        color = light_dict["color"]
        if "intensity" in light_dict.keys():
            if isinstance(light_dict["intensity"], int): 
                intensity = light_dict["intensity"]
            else: 
                assert len(light_dict["intensity"]) == 1, "Animating light intensity is not yet supported."
                intensity = light_dict["intensity"][0]
        else:
            print("Light intensity not specified. Setting to 5.")
            intensity = 5
        if "visible" in light_dict.keys():
            if isinstance(light_dict["visible"], int): 
                visible = light_dict["visible"]
            else: 
                assert len(light_dict["visible"]) == 1, "Animating light visible is not yet supported."
                visible = light_dict["visible"][0]
        else:
            print("Light visibility not specified. Setting to 1.")
            visible = 1
        pos = [light_dict["position"]["x"],
               light_dict["position"]["y"], 
               light_dict["position"]["z"]]
        num_pos_stimuli = max([len(pos[i]) for i in range(3)])
        num_stimuli = num_pos_stimuli
        for i in range(3):
            if len(pos[i]) == 1: pos[i] = pos[i]*num_stimuli
        light = Light(name, light_type, color, intensity, visible)
        light.set_position(pos)
        return light
    
class Object:

    def __init__(self, name="obj", meshpath="/", 
                 objectdoc=None, 
                 texture=True,
                 material_type="MeshPhysicalMaterial", 
                 material_color=0x7F7F7F,
                 material_metalness=0.25,
                 material_roughness=0.65,
                 material_reflectivity=0.5,
                 material_opacity=1,
                 material_transparent=False):
        self.name = name
        self.meshpath = meshpath
        self.objectdoc = objectdoc
        self.texture = texture
        self.material_type = material_type
        self.material_color = material_color
        self.material_metalness = material_metalness
        self.material_roughness = material_roughness
        self.material_reflectivity = material_reflectivity
        self.material_opacity = material_opacity
        self.material_transparent = material_transparent

        self.num_stimuli = 1
        self.size = [0]*self.num_stimuli
        self.position = [[0]*self.num_stimuli] * 3
        self.rotation = [[0]*self.num_stimuli] * 3
        self.visible = [0]*self.num_stimuli
        self.target = [0]*self.num_stimuli

    def set_size(self, size):
        self.size = size
        self.num_stimuli = max(self.num_stimuli, len(size))

    def set_position(self, position):
        assert len(position) == 3, "Position must be given as (x, y, z)!"
        assert len(position[0]) == len(position[1]) == len(position[2]), "(x, y, z) stimulus lengths must match!"
        self.position = position
        self.num_stimuli = max(self.num_stimuli, len(position[0]))

    def set_rotation(self, rotation):
        assert len(rotation) == 3, "Rotation must be given as (x, y, z)!"
        assert len(rotation[0]) == len(rotation[1]) == len(rotation[2]), "(x, y, z) stimulus lengths must match!"
        self.rotation = rotation
        self.num_stimuli = max(self.num_stimuli, len(rotation[0]))

    def set_visible(self, visible):
        self.visible = visible
        self.num_stimuli = max(self.num_stimuli, len(visible))

    def set_target(self, target):
        self.target = target
        self.num_stimuli = max(self.num_stimuli, len(target))

    def is_consistent(self):
        return len(self.size) == len(self.position[0]) == len(self.rotation[0]) \
            == len(self.visible) == len(self.target) == self.num_stimuli
    
    def duplicate(self, factor):
        self.set_size(self.size*factor)
        self.set_position([self.position[i]*factor for i in range(3)])
        self.set_rotation([self.rotation[i]*factor for i in range(3)])
        self.set_visible(self.visible*factor)
        self.set_target(self.target*factor)

    def copy(self):
        obj = Object(self.name, self.meshpath, self.objectdoc,
                         self.texture, self.material_type,
                         self.material_color, self.material_metalness,
                         self.material_roughness, self.material_reflectivity,
                         self.material_opacity, self.material_transparent)
        obj.set_size(self.size.copy())
        obj.set_position(self.position.copy())
        obj.set_rotation(self.rotation.copy())
        obj.set_visible(self.visible.copy())
        obj.set_target(self.target.copy())
        return obj

    def subset(self, i, j):
        assert i <= j and i >= 0 and j <= self.num_stimuli, "Improper indices for subset, please try again!"
        sub_obj = Object(self.name, self.meshpath, self.objectdoc,
                         self.texture, self.material_type,
                         self.material_color, self.material_metalness,
                         self.material_roughness, self.material_reflectivity,
                         self.material_opacity, self.material_transparent)
        sub_obj.set_size(self.size[i:j+1])
        sub_obj.set_position([self.position[k][i:j+1] for k in range(3)])
        sub_obj.set_rotation([self.rotation[k][i:j+1] for k in range(3)])
        sub_obj.set_visible(self.visible[i:j+1])
        sub_obj.set_target(self.target[i:j+1])
        return sub_obj

    def concatenate(o1, o2):
        assert o1.is_consistent() and o2.is_consistent(), "Objects must be consistent to concatenate!"
        assert o1.name == o2.name, "Object names must match!"
        assert o1.meshpath == o2.meshpath, "Object meshpaths must match!"
        assert o1.objectdoc == o2.objectdoc, "Object objectdocs must match!"
        assert o1.texture == o2.texture, "Object textures must match!"
        assert o1.material_type == o2.material_type, "Object material types must match!"
        assert o1.material_color == o2.material_color, "Object material colors must match!"
        assert o1.material_metalness == o2.material_metalness, "Object material metalnesses must match!"
        assert o1.material_roughness == o2.material_roughness, "Object material roughnesses must match!"
        assert o1.material_reflectivity == o2.material_reflectivity, "Object material reflectivities must match!"
        assert o1.material_opacity == o2.material_opacity, "Object material opacities must match!"
        assert o1.material_transparent == o2.material_transparent, "Object material transparents must match!"
        obj = Object(o1.name, o1.meshpath, o1.objectdoc, o1.texture,
                     o1.material_type, o1.material_color,
                     o1.material_metalness,
                     o1.material_roughness, 
                     o1.material_reflectivity,
                     o1.material_opacity,
                     o1.material_transparent)
        obj.set_size(o1.size + o2.size)
        obj.set_position([o1.position[i] + o2.position[i] for i in range(3)])
        obj.set_rotation([o1.rotation[i] + o2.rotation[i] for i in range(3)])
        obj.set_visible(o1.visible + o2.visible)
        obj.set_target(o1.target + o2.target)
        assert obj.num_stimuli == o1.num_stimuli + o2.num_stimuli, "Concatenation must sum object stimulus counts."
        return obj

    def to_dict(self):
        obj_dict = {"meshpath": self.meshpath,
                    "objectdoc": self.objectdoc,
                    "texture": self.texture,
                    "material": {
                        "type": self.material_type,
                        "color": self.material_color,
                        "metalness": self.material_metalness,
                        "roughness": self.material_roughness,
                        "reflectivity": self.material_reflectivity,
                        "opacity": [self.material_opacity],
                        "transparent": self.material_transparent
                    },
                    "sizeTHREEJS": self.size,
                    "positionTHREEJS": {"x": self.position[0],
                                 "y": self.position[1],
                                 "z": self.position[2]},
                    "rotationDegrees": {"x": self.rotation[0],
                                 "y": self.rotation[1],
                                 "z": self.rotation[2]},
                    "visible": self.visible,
                    "target": self.target}
        return obj_dict
    
    def from_dict(obj_dict, name):
        meshpath = obj_dict["meshpath"]
        objectdoc = obj_dict["objectdoc"]
        texture = obj_dict["texture"]
        material_type = obj_dict["material"]["type"]
        material_color = obj_dict["material"]["color"]
        material_metalness = obj_dict["material"]["metalness"]
        material_roughness = obj_dict["material"]["roughness"]
        material_reflectivity = obj_dict["material"]["reflectivity"]
        if "opacity" in obj_dict["material"].keys():
            if isinstance(obj_dict["material"]["opacity"], int) or isinstance(obj_dict["material"]["opacity"], float): 
                material_opacity = obj_dict["material"]["opacity"]
            else: 
                assert len(obj_dict["material"]["opacity"]) == 1, "Animating object material opacity is not yet supported."
                material_opacity = obj_dict["material"]["opacity"][0]
        else:
            print(f"Material opacity for object {name} not specified. Setting to 1.")
            material_opacity = 1
        material_transparent = obj_dict["material"]["transparent"]
        sizes = obj_dict["sizeTHREEJS"]
        positions = [obj_dict["positionTHREEJS"]["x"],
                     obj_dict["positionTHREEJS"]["y"],
                     obj_dict["positionTHREEJS"]["z"]]
        rotations = [obj_dict["rotationDegrees"]["x"],
                     obj_dict["rotationDegrees"]["y"],
                     obj_dict["rotationDegrees"]["z"]]
        if "visible" in obj_dict.keys():
            if isinstance(obj_dict["visible"], int): 
                visibles = [obj_dict["visible"]]
            else: 
                visibles = obj_dict["visible"]
        else: 
            print(f"Visibility for object {name} not specified. Setting to [1].")
            visibles = [1]
        if "target" in obj_dict.keys():
            if isinstance(obj_dict["target"], int): 
                targets = [obj_dict["target"]]
            else: 
                targets = obj_dict["target"]
        else:
            print(f"Target status for object {name} not found. Setting to [1].")
            targets = [1]
        num_size_stimuli = len(sizes)
        num_pos_stimuli = max([len(positions[i]) for i in range(3)])
        num_rot_stimuli = max([len(rotations[i]) for i in range(3)])
        num_vis_stimuli = len(visibles)
        num_tgt_stimuli = len(targets)
        num_stimuli = max(num_size_stimuli, num_pos_stimuli, num_rot_stimuli,
                          num_vis_stimuli, num_tgt_stimuli)
        if num_size_stimuli == 1: sizes = sizes * num_stimuli
        for i in range(3):
            if len(positions[i]) == 1: positions[i] = positions[i]*num_stimuli
            if len(rotations[i]) == 1: rotations[i] = rotations[i]*num_stimuli
        if num_vis_stimuli == 1: visibles = visibles * num_stimuli
        if num_tgt_stimuli == 1: targets = targets * num_stimuli
        object = Object(name, meshpath, objectdoc, texture,
                        material_type, material_color,
                        material_metalness, material_roughness,
                        material_reflectivity, material_opacity,
                        material_transparent)
        object.set_size(sizes)
        object.set_position(positions)
        object.set_rotation(rotations)
        object.set_visible(visibles)
        object.set_target(targets)
        return object

class Image:

    def __init__(self, name="img",
                 imagebag="/mkturkfiles/assets/polyhaven/",
                 img_size=10):
        self.name = name
        self.imagebag = imagebag
        self.num_stimuli = 1
        self.imageidx = [0]*self.num_stimuli
        self.visible = [1]*self.num_stimuli
        self.size = img_size

    def set_imageidx(self, imageidx):
        self.imageidx = imageidx
        self.num_stimuli = max(self.num_stimuli, len(imageidx))
    
    def set_visible(self, visible):
        self.visible = visible
        self.num_stimuli = max(self.num_stimuli, len(visible))

    def is_consistent(self):
        return len(self.imageidx) == len(self.visible) == self.num_stimuli
    
    def duplicate(self, factor):
        self.set_imageidx(self.imageidx*factor)
        self.set_visible(self.visible*factor)

    def copy(self):
        img = Image(self.name, self.imagebag, self.size)
        imageidx = self.imageidx.copy()
        visible = self.visible.copy()
        img.set_imageidx(imageidx)
        img.set_visible(visible)
        return img

    def subset(self, i, j):
        assert i <= j and i >= 0 and j <= self.num_stimuli, "Improper indices for subset, please try again!"
        sub_img = Image(self.name, self.imagebag, self.size)
        sub_img.set_imageidx(self.imageidx[i:j+1])
        sub_img.set_visible(self.visible[i:j+1])
        return sub_img
    
    def concatenate(img1, img2):
        assert img1.is_consistent() and img2.is_consistent(), "Images must be consistent to concatenate!"
        assert img1.name == img2.name, "Image names must match!"
        assert img1.imagebag == img2.imagebag, "Imagebags must match!"
        assert img1.size == img2.size, "Image sizes must match!"
        img = Image(img1.name, img1.imagebag, img1.size)
        img.set_imageidx(img1.imageidx + img2.imageidx)
        img.set_visible(img1.visible + img2.visible)
        return img

    def to_dict(self):
        img_dict = {"imagebag": self.imagebag,
                    "imageidx": self.imageidx,
                    "visible": self.visible,
                    "sizeTHREEJS": self.size}
        return img_dict

    def from_dict(img_dict, name):
        imagebag = img_dict["imagebag"]
        if "imageidx" in img_dict.keys():
            if isinstance(img_dict["imageidx"], int):
                imageidx = [img_dict["imageidx"]]
            else:
                assert len(img_dict["imageidx"]) > 0, "List of background indices is empty! Please set the background to some default value, and turn off its visibility." 
                imageidx = img_dict["imageidx"] 
        else:
            assert "Background indices must be specified! Please try again."
        if "visible" in img_dict.keys():
            if isinstance(img_dict["visible"], int): 
                visible = [img_dict["visible"]]
            else: 
                visible = img_dict["visible"]
        else:
            print("Background visibility not specified. Setting to [1].")
            visible = [1]
        num_stimuli = max(len(imageidx), len(visible))
        if len(imageidx) == 1: imageidx = imageidx * num_stimuli
        if len(visible) == 1: visible = visible * num_stimuli
        img_size = img_dict["sizeTHREEJS"][0] #TODO: Add similar handling for img_size, and for other params across scenefile
        img = Image(name, imagebag, img_size)
        img.set_imageidx(imageidx)
        img.set_visible(visible)
        return img

class Filters:

    def __init__(self, name="filters", default_blur=0, default_brightness=1, 
                 default_contrast=1, default_grayscale=0,
                 default_huerotate=0, default_invert=0, default_opacity=1, 
                 default_saturate=1, default_sepia=0):
        self.name = name
        self.num_stimuli = 1
        self.blur = [default_blur]
        self.brightness = [default_brightness]
        self.contrast = [default_contrast]
        self.grayscale = [default_grayscale]
        self.huerotate = [default_huerotate]
        self.invert = [default_invert]
        self.opacity = [default_opacity]
        self.saturate = [default_saturate]
        self.sepia = [default_sepia]
    
    def get_filter_maps(self):
        return (self.blur, self.brightness, self.contrast, self.grayscale,
                self.huerotate, self.invert, self.opacity,
                self.saturate, self.sepia)

    def set_blur(self, blur):
        self.blur = blur
        self.num_stimuli = max(self.num_stimuli, len(blur))

    def set_brightness(self, brightness):
        self.brightness = brightness
        self.num_stimuli = max(self.num_stimuli, len(brightness))

    def set_contrast(self, contrast):
        self.contrast = contrast
        self.num_stimuli = max(self.num_stimuli, len(contrast))

    def set_grayscale(self, grayscale):
        self.grayscale = grayscale
        self.num_stimuli = max(self.num_stimuli, len(grayscale))

    def set_huerotate(self, huerotate):
        self.huerotate = huerotate
        self.num_stimuli = max(self.num_stimuli, len(huerotate))

    def set_invert(self, invert):
        self.invert = invert
        self.num_stimuli = max(self.num_stimuli, len(invert))

    def set_opacity(self, opacity):
        self.opacity = opacity
        self.num_stimuli = max(self.num_stimuli, len(opacity))

    def set_saturate(self, saturate):
        self.saturate = saturate
        self.num_stimuli = max(self.num_stimuli, len(saturate))

    def set_sepia(self, sepia):
        self.sepia = sepia
        self.num_stimuli = max(self.num_stimuli, len(sepia))

    def is_consistent(self):
        return len(self.blur) == len(self.brightness) == len(self.contrast) \
            == len(self.grayscale) == len(self.huerotate) == len(self.invert) \
            == len(self.opacity) == len(self.saturate) == len(self.sepia) == self.num_stimuli
    
    def duplicate(self, factor):
        self.set_blur(self.blur * factor)
        self.set_brightness(self.brightness * factor)
        self.set_contrast(self.contrast * factor)
        self.set_grayscale(self.grayscale * factor)
        self.set_huerotate(self.huerotate * factor)
        self.set_invert(self.invert * factor)
        self.set_opacity(self.opacity * factor)
        self.set_saturate(self.saturate * factor)
        self.set_sepia(self.sepia * factor)
    
    def copy(self):
        filters = Filters(self.name)
        filters.set_blur(self.blur.copy())
        filters.set_brightness(self.brightness.copy())
        filters.set_contrast(self.contrast.copy())
        filters.set_grayscale(self.grayscale.copy())
        filters.set_huerotate(self.huerotate.copy())
        filters.set_invert(self.invert.copy())
        filters.set_opacity(self.opacity.copy())
        filters.set_saturate(self.saturate.copy())
        filters.set_sepia(self.sepia.copy())
        return filters
    
    def subset(self, i, j):
        assert i <= j and i >= 0 and j <= self.num_stimuli, "Improper indices for subset, please try again!"
        sub_filters = Filters(self.name)
        sub_filters.set_blur(self.blur[i:j+1])
        sub_filters.set_brightness(self.contrast[i:j+1])
        sub_filters.set_contrast(self.contrast[i:j+1])
        sub_filters.set_grayscale(self.grayscale[i:j+1])
        sub_filters.set_huerotate(self.huerotate[i:j+1])
        sub_filters.set_invert(self.invert[i:j+1])
        sub_filters.set_opacity(self.opacity[i:j+1])
        sub_filters.set_saturate(self.saturate[i:j+1])
        sub_filters.set_sepia(self.sepia[i:j+1])
        return sub_filters
    
    def concatenate(filter1, filter2):
        assert filter1.is_consistent() and filter2.is_consistent(), "Filters must be consistent to concatenate!"
        assert filter1.name == filter2.name, "Filter names must match to concatenate!"
        filter = Filters(filter1.name)
        filter.set_blur(filter1.blur + filter2.blur)
        filter.set_brightness(filter1.brightness + filter2.brightness)
        filter.set_contrast(filter1.contrast + filter2.contrast)
        filter.set_grayscale(filter1.grayscale + filter2.grayscale)
        filter.set_huerotate(filter1.huerotate + filter2.huerotate)
        filter.set_opacity(filter1.opacity + filter2.opacity)
        filter.set_invert(filter1.invert + filter2.invert)
        filter.set_saturate(filter1.saturate + filter2.saturate)
        filter.set_sepia(filter1.sepia + filter2.sepia)
        return filter

    def to_dict(self):
        filter_dict = {"blur": self.blur,
                       "brightness": self.brightness,
                       "contrast": self.contrast,
                       "grayscale": self.grayscale,
                       "huerotate": self.huerotate,
                       "invert": self.invert,
                       "opacity": self.opacity,
                       "saturate": self.saturate,
                       "sepia": self.sepia}
        return filter_dict
    
    def from_dict(filter_dict, name):
        blur = filter_dict["blur"]
        brightness = filter_dict["brightness"]
        contrast = filter_dict["contrast"]
        grayscale = filter_dict["grayscale"]
        huerotate = filter_dict["huerotate"]
        invert = filter_dict["invert"]
        opacity = filter_dict["opacity"]
        saturate = filter_dict["saturate"]
        sepia = filter_dict["sepia"]
        filters = Filters(name)
        if len(blur) != 0: filters.set_blur(blur)
        if len(brightness) != 0: filters.set_brightness(brightness)
        if len(contrast) != 0: filters.set_contrast(contrast)
        if len(grayscale) != 0: filters.set_grayscale(grayscale)
        if len(huerotate) != 0: filters.set_huerotate(huerotate)
        if len(invert) != 0: filters.set_invert(invert)
        if len(opacity) != 0: filters.set_opacity(opacity)
        if len(saturate) != 0: filters.set_saturate(saturate)
        if len(sepia) != 0: filters.set_sepia(sepia)
        num_stimuli = max(len(filters.blur), len(filters.brightness), len(filters.contrast), 
                          len(filters.grayscale), len(filters.huerotate), len(filters.invert), 
                          len(filters.opacity), len(filters.saturate), len(filters.sepia))
        if len(filters.blur) == 1: filters.blur = filters.blur * num_stimuli
        if len(filters.brightness) == 1: filters.brightness = filters.brightness * num_stimuli
        if len(filters.contrast) == 1: filters.contrast = filters.contrast * num_stimuli
        if len(filters.grayscale) == 1: filters.grayscale = filters.grayscale * num_stimuli
        if len(filters.huerotate) == 1: filters.huerotate = filters.huerotate * num_stimuli
        if len(filters.invert) == 1: filters.invert = filters.invert * num_stimuli
        if len(filters.opacity) == 1: filters.opacity = filters.opacity * num_stimuli
        if len(filters.saturate) == 1: filters.saturate = filters.saturate * num_stimuli
        if len(filters.sepia) == 1: filters.sepia = filters.sepia * num_stimuli
        return filters


class Scenefile:

    def __init__(self, cameras=None, lights=None, objects=None, img=None, obj_filters=None, img_filters=None, num_stimuli=1, duration=100):
        self.cameras = cameras if cameras is not None else []
        self.lights = lights if lights is not None else []
        self.objects = objects if objects is not None else []
        self.img = img
        self.obj_filters = obj_filters
        self.img_filters = img_filters
        self.num_stimuli = num_stimuli
        self.duration = duration
    
    def get_elements(self):
        return *self.cameras, *self.lights, *self.objects, self.img, self.obj_filters, self.img_filters
    
    def get_element_names(self):
        return [[cam.name for cam in self.cameras], [light.name for light in self.lights],
                [obj.name for obj in self.objects], self.img.name, self.obj_filters.name, self.img_filters.name]
    
    def get_camera(self, cam_name):
        for cam in self.cameras:
            if cam.name == cam_name: return cam
        return None

    def get_light(self, light_name):
        for light in self.lights:
            if light.name == light_name: return light
        return None
    
    def get_object(self, obj_name):
        for obj in self.objects:
            if obj.name == obj_name: return obj
        return None
    
    def get_image(self, img_name="img"):
        assert img_name == "img", "Each Scenefile contains only one Image, which must have name \'img\'."
        return self.img
    
    def get_object_filters(self):
        return self.obj_filters
    
    def get_image_filters(self):
        return self.img_filters
    
    def get_filters(self, filters_name):
        assert filters_name in ["obj_filters", "img_filters"], "Each Scenefile only contains two Filters with names \'obj_filters\' and \'img_filters\'."
        if filters_name == "obj_filters":
            return self.get_object_filters()
        if filters_name == "img_filters":
            return self.get_image_filters()

    def is_consistent(self):
        print("Initiating scenefile consistency check.")
        flag = True
        names = []
        for scene_element in self.get_elements():
            name_flag = not (scene_element.name in names)
            if name_flag: names.append(scene_element.name)
            else: print("Name", scene_element.name)
            elt_flag = scene_element.num_stimuli == self.num_stimuli
            new_flag = elt_flag and name_flag and scene_element.is_consistent()
            flag = flag and new_flag
            if not new_flag: print(f"Consistency broken by {scene_element}!", name_flag, elt_flag, scene_element.is_consistent())
        if flag: print("Consistency check passed!")
        return flag
    
    def duplicate(self, factor):
        for camera in self.cameras:
            camera.duplicate(factor)
        for light in self.lights:
            light.duplicate(factor)
        for object in self.objects:
            object.duplicate(factor)
        self.img.duplicate(factor)
        self.obj_filters.duplicate(factor)
        self.img_filters.duplicate(factor)
        self.num_stimuli *= factor
        assert self.is_consistent()

    def copy(self):
        cams = [cam.copy() for cam in self.cameras]
        lights = [light.copy() for light in self.lights]
        objects = [obj.copy() for obj in self.objects]
        img = self.img.copy()
        obj_filters = self.obj_filters.copy()
        img_filters = self.img_filters.copy()
        scenefile = Scenefile(cams, lights, objects,
                                  img, obj_filters, img_filters,
                                  self.num_stimuli, self.duration)
        return scenefile
    
    def subset(self, i, j):
        assert i <= j and i >= 0 and j <= self.num_stimuli, "Improper indices for subset, please try again!"
        sub_cams = [cam.subset(i, j) for cam in self.cameras]
        sub_lights = [light.subset(i, j) for light in self.lights]
        sub_objects = [obj.subset(i, j) for obj in self.objects]
        sub_img = self.img.subset(i, j)
        sub_obj_filters = self.obj_filters.subset(i, j)
        sub_img_filters = self.img_filters.subset(i, j)
        sub_scenefile = Scenefile(sub_cams, sub_lights, sub_objects,
                                  sub_img, sub_obj_filters, sub_img_filters,
                                  j - i + 1, self.duration)
        assert sub_scenefile.is_consistent(), "Subset scenefile is not consistent!"
        return sub_scenefile
    
    def concatenate(scenefile1, scenefile2):
        assert scenefile1.is_consistent() and scenefile2.is_consistent(), "Scenefiles must both be consistent to concatenate!"
        assert scenefile1.duration == scenefile2.duration, "Durations must match for concatenation!"
        cameras = []
        for cam1 in scenefile1.cameras:
            concatenated = False
            for cam2 in scenefile2.cameras:
                if cam1.name == cam2.name: 
                    cameras.append(Camera.concatenate(cam1, cam2))
                    concatenated = True
            if not concatenated:
                cameras.append(Camera.concatenate(cam1, cam1.subset(0,0).duplicate(cam2.num_stimuli)))
        for cam2 in scenefile2.cameras:
            concatenated = False
            for cam1 in scenefile1.cameras:
                if cam1.name == cam2.name: concatenated = True
            if not concatenated:
                cameras.append(Camera.concatenate(cam2.subset(0,0).duplicate(cam1.num_stimuli), cam2))       
        lights = []
        for light1 in scenefile1.lights:
            concatenated = False
            for light2 in scenefile2.lights:
                if light1.name == light2.name: 
                    lights.append(Light.concatenate(light1, light2))
                    concatenated = True
            if not concatenated:
                lights.append(Light.concatenate(light1, light1.subset(0,0).duplicate(light2.num_stimuli)))
        for light2 in scenefile2.lights:
            concatenated = False
            for light1 in scenefile1.lights:
                if light1.name == light2.name: concatenated = True
            if not concatenated:
                lights.append(Light.concatenate(light2.subset(0,0).duplicate(light1.num_stimuli), light2))   
        objects = []
        for obj1 in scenefile1.objects:
            concatenated = False
            for obj2 in scenefile2.objects:
                if obj1.name == obj2.name: 
                    objects.append(Object.concatenate(obj1, obj2))
                    concatenated = True
            if not concatenated:
                objects.append(Object.concatenate(obj1, obj1.subset(0,0).duplicate(obj2.num_stimuli)))
        for obj2 in scenefile2.objects:
            concatenated = False
            for obj1 in scenefile1.objects:
                if obj1.name == obj2.name: concatenated = True
            if not concatenated:
                objects.append(Object.concatenate(obj2.subset(0,0).duplicate(obj1.num_stimuli), obj2))   
        img = Image.concatenate(scenefile1.img, scenefile2.img)
        obj_filters = Filters.concatenate(scenefile1.obj_filters, scenefile2.obj_filters)
        img_filters = Filters.concatenate(scenefile1.img_filters, scenefile2.img_filters)
        scenefile = Scenefile(cameras, lights, objects,
                              img, obj_filters, img_filters,
                              scenefile1.num_stimuli + scenefile2.num_stimuli, 
                              scenefile1.duration)
        assert scenefile.is_consistent(), "Concatenated scenefile not consistent!"
        return scenefile

    def from_json(json_path, check_consistency=True):

        scenefile = Scenefile()

        with open(json_path, "r") as sf:
            scene_dict = json.load(sf)

        num_stimuli = 0

        print("Loading camera!")
        cam_dict = scene_dict["CAMERAS"]
        for cam_name in cam_dict.keys():
            scenefile.cameras.append(Camera.from_dict(cam_dict[cam_name], cam_name))
        for camera in scenefile.cameras:
            assert camera.is_consistent(), "Camera not consistent!"
        num_stimuli = max(num_stimuli, *[cam.num_stimuli for cam in scenefile.cameras])
        print(f"Camera loading done. Number of stimuli at {num_stimuli}.")

        print("Loading lights!")
        light_dict = scene_dict["LIGHTS"]
        for light_name in light_dict.keys():
            scenefile.lights.append(Light.from_dict(light_dict[light_name], light_name))
        for light in scenefile.lights:
            assert light.is_consistent(), "Light not consistent!"
        num_stimuli = max(num_stimuli, *[light.num_stimuli for light in scenefile.lights])
        print(f"Light loading done. Number of stimuli at {num_stimuli}.")

        print("Loading objects!")
        obj_dict = scene_dict["OBJECTS"]
        for obj_name in obj_dict.keys():
            scenefile.objects.append(Object.from_dict(obj_dict[obj_name], obj_name))
        for obj in scenefile.objects:
            assert obj.is_consistent(), "Object not consistent!"
        num_stimuli = max(num_stimuli, *[obj.num_stimuli for obj in scenefile.objects])
        print(f"Object loading done. Number of stimuli at {num_stimuli}.")

        print("Loading images!")
        img_dict = scene_dict["IMAGES"]
        scenefile.img = Image.from_dict(img_dict, "img")
        assert scenefile.img.is_consistent(), "Images not consistent!"
        print(f"Images done. Number of stimuli at {num_stimuli}.")

        print("Loading object filters!")
        obj_filter_dict = scene_dict["OBJECTFILTERS"]
        scenefile.obj_filters = Filters.from_dict(obj_filter_dict, "obj_filters")
        assert scenefile.obj_filters.is_consistent(), "Object filters not consistent!"
        print(f"Object filter loading done. Number of stimuli at {num_stimuli}.")
    
        print("Loading image filters!")
        img_filter_dict = scene_dict["IMAGEFILTERS"]
        scenefile.img_filters = Filters.from_dict(img_filter_dict, "img_filters")
        assert scenefile.img_filters.is_consistent(), "Image filters not consistent!"
        print(f"Image filter loading done. Number of stimuli at {num_stimuli}.")

        scenefile.num_stimuli = num_stimuli

        for scene_element in scenefile.get_elements():
            if scene_element.num_stimuli == 1:
                scene_element.duplicate(num_stimuli)
            if check_consistency:
                assert scene_element.num_stimuli == scenefile.num_stimuli, "Scene elements should have either one or all stimuli, nothing in between."

        print(scenefile.get_elements())
        if check_consistency:
            assert scenefile.is_consistent(), "Scenefile not consistent! Please try again."

        scenefile.duration = scene_dict["durationMS"]

        return scenefile

    def to_json(self, json_path, indent=1):

        scene_dict = {"CAMERAS": None, "LIGHTS": None, 
                      "OBJECTS": None, "IMAGES": None,
                      "OBJECTFILTERS": None,
                      "IMAGEFILTERS": None,
                      "durationMS": 0}

        scene_dict["CAMERAS"] = {}
        for cam in self.cameras:
            scene_dict["CAMERAS"][cam.name] = cam.to_dict()
        scene_dict["LIGHTS"] = {}
        for light in self.lights:
            scene_dict["LIGHTS"][light.name] = light.to_dict()
        scene_dict["OBJECTS"] = {}
        for obj in self.objects:
            scene_dict["OBJECTS"][obj.name] = obj.to_dict()
        scene_dict["IMAGES"] = self.img.to_dict()
        scene_dict["OBJECTFILTERS"] = self.obj_filters.to_dict()
        scene_dict["IMAGEFILTERS"] = self.img_filters.to_dict()

        scene_dict["durationMS"] = self.duration

        with open(json_path, "w") as outfile:
            json.dump(scene_dict, outfile, indent=indent)

    def apply_animation(scene, animation, base):
        print("Applying animation", animation, ".")
        assert scene.is_consistent(), "Scene must be consistent to animate!"
        add_scene = base.copy()
        if isinstance(animation, Animation):
            animation = [animation]
        add_scene.duplicate(animation[0].num_stimuli)
        for anim in animation:
            anim_element = Animation.animations[anim.param][0](add_scene, anim.element_name)
            Animation.animations[anim.param][1](anim_element, anim.range)
        # pprint.pprint(anim_element.to_dict())
        return Scenefile.concatenate(scene, add_scene)
        

class Animation:

    animations = {"cam:pos" : (Scenefile.get_camera, Camera.set_position), 
                  "cam:tgt" : (Scenefile.get_camera, Camera.set_target), 
                  "light:pos" : (Scenefile.get_light, Light.set_position), 
                  "obj:size" : (Scenefile.get_object, Object.set_size), 
                  "obj:pos" : (Scenefile.get_object, Object.set_position), 
                  "obj:rot" : (Scenefile.get_object, Object.set_rotation), 
                  "obj:vis" : (Scenefile.get_object, Object.set_visible), 
                  "obj:tgt" : (Scenefile.get_object, Object.set_target), 
                  "img:idx" : (Scenefile.get_image, Image.set_imageidx), 
                  "img:vis" : (Scenefile.get_image, Image.set_visible), 
                  "filt:blu" : (Scenefile.get_filters, Filters.set_blur), 
                  "filt:bri" : (Scenefile.get_filters, Filters.set_brightness), 
                  "filt:con" : (Scenefile.get_filters, Filters.set_contrast),
                  "filt:gra" : (Scenefile.get_filters, Filters.set_grayscale), 
                  "filt:hue" : (Scenefile.get_filters, Filters.set_huerotate), 
                  "filt:inv" : (Scenefile.get_filters, Filters.set_invert),
                  "filt:opa" : (Scenefile.get_filters, Filters.set_opacity), 
                  "filt:sat" : (Scenefile.get_filters, Filters.set_saturate), 
                  "filt:sep" : (Scenefile.get_filters, Filters.set_sepia)}
    
    xyz_params = ["cam:pos", "cam:tgt", "light:pos", "obj:pos", "obj:rot"]

    def __init__(self, param, range, element_name):
        self.param = param
        assert param in Animation.animations.keys(), "Specified param not recognized, please try again!"
        self.range = range
        if param in Animation.xyz_params:
            assert len(self.range[0]) == len(self.range[1]) == len(self.range[2]), "(x, y, z) animation lengths must match!"
            self.num_stimuli = len(self.range[0])
        else: self.num_stimuli = len(self.range)
        self.element_name = element_name


class ScenefileSchema:

    def __init__(self, base):
        self.base = base
        assert self.base.num_stimuli == 1, "Base must be a single-stimulus scenefile!"
        self.animations = []
        self.num_animations = 1

    def is_consistent(animations):
        if len(animations) == 0: return True
        num_stimuli = animations[0].num_stimuli
        for anim in animations:
            if anim.num_stimuli != num_stimuli: return False
        return True

    def add_animations(self, animations):
        for anim in animations:
            if isinstance(anim, Animation):
                self.animations.append(anim)
                self.num_animations += 1
            else:
                assert isinstance(anim, list), "All animations must be single animations or lists!"
                assert len(anim) > 0, "Animations list is empty."
                assert ScenefileSchema.is_consistent(anim), "Parallel animations must have the same number of stimuli!"
                self.animations.append(anim)
                self.num_animations += 1

    def generate_scenefile(self):
        scenefile = self.base.copy()
        for anim in self.animations:
            scenefile = Scenefile.apply_animation(scenefile, anim, self.base)
        return scenefile
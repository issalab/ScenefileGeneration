import os
import json
import numpy as np

#TODO: Add the ability to include arbitrarily many objects, cameras, lights
#TODO: Add the ability to animate filter params.
#TODO: Add flags to accurately maintain the number of stimuli within and across scene elements.
#TODO: Abstract the logic of scene element into a separate class.
#TODO: Include ability to save out scenefile to JSON.
#TODO: Change np arrays to Python lists to enable animation of movies.

class Camera:

    def __init__(self,
                 camera_type="PerspectiveCamera", 
                 fov=45, near=0.1, far=2000, visible=1):
        self.camera_type = camera_type
        self.field_of_view = fov
        self.near = near
        self.far = far
        self.num_stimuli = 1
        self.position = np.zeros((3, self.num_stimuli))
        self.target = np.zeros((3, self.num_stimuli))
        self.visible = visible

    def set_position(self, position):
        # Must input expanded array of positions!
        self.position = position
        self.num_stimuli = max(self.num_stimuli, position.shape[1])
    
    def set_target(self, target):
        self.target = target
        self.num_stimuli = max(self.num_stimuli, target.shape[1])

    def to_dict(self):
        cam_dict = {"type": self.camera_type,
                    "fieldOfView": self.field_of_view,
                    "near": self.near,
                    "far": self.far,
                    "position": {"x": self.position[0].tolist(),
                                 "y": self.position[1].tolist(),
                                 "z": self.position[2].tolist()},
                    "targetTHREEJS": {"x": self.target[0].tolist(),
                                 "y": self.target[1].tolist(),
                                 "z": self.target[2].tolist()},
                    "visible": [self.visible]}
        return cam_dict
    
    def from_dict(cam_dict):
        camera_type = cam_dict["type"]
        field_of_view = cam_dict["fieldOfView"]
        near = cam_dict["near"]
        far = cam_dict["far"]
        visible = cam_dict["visible"][0]
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
        position = np.array(pos)
        target = np.array(tgt)
        camera = Camera(camera_type,
                        field_of_view,
                        near, far,
                        visible)
        camera.set_position(position)
        camera.set_target(target)
        return camera
    
class Light:

    def __init__(self, light_type, color=0xffffff, intensity=5, visible=1):
        self.light_type = light_type
        self.color = color
        self.intensity = intensity
        self.visible = visible
        self.num_stimuli = 1
        self.position = np.zeros((3, self.num_stimuli))

    def set_position(self, position):
        # Must input expanded array of positions!
        self.position = position
        self.num_stimuli = max(self.num_stimuli, position.shape[1])

    def to_dict(self):
        light_dict = {"type": self.light_type,
                    "color": self.color,
                    "intensity": [self.intensity],
                    "position": {"x": self.position[0].tolist(),
                                 "y": self.position[1].tolist(),
                                 "z": self.position[2].tolist()},
                    "visible": [self.visible]}
        return light_dict
    
    def from_dict(light_dict):
        light_type = light_dict["type"]
        color = light_dict["color"]
        intensity = light_dict["intensity"][0]
        visible = light_dict["visible"][0]
        pos = [light_dict["position"]["x"],
               light_dict["position"]["y"], 
               light_dict["position"]["z"]]
        num_pos_stimuli = max([len(pos[i]) for i in range(3)])
        num_stimuli = num_pos_stimuli
        for i in range(3):
            if len(pos[i]) == 1: pos[i] = pos[i]*num_stimuli
        position = np.array(pos)
        light = Light(light_type, color, intensity, visible)
        light.set_position(position)
        return light
    
class Object:

    def __init__(self, meshpath, 
                 objectdoc=None, 
                 texture=True,
                 material_type="MeshPhysicalMaterial", 
                 material_color=0x7F7F7F,
                 material_metalness=0.25,
                 material_roughness=0.65,
                 material_reflectivity=0.5,
                 material_opacity=1,
                 material_transparent=False):
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
        self.size = np.zeros(self.num_stimuli)
        self.position = np.zeros((3, self.num_stimuli))
        self.rotation = np.zeros((3, self.num_stimuli))
        self.visible = np.zeros(self.num_stimuli, dtype="int")
        self.target = np.zeros(self.num_stimuli, dtype="int")

    def set_size(self, sizes):
        self.size = sizes
        self.num_stimuli = max(self.num_stimuli, sizes.shape[0])

    def set_position(self, positions):
        self.position = positions
        self.num_stimuli = max(self.num_stimuli, positions.shape[1])

    def set_rotation(self, rotations):
        self.rotation = rotations
        self.num_stimuli = max(self.num_stimuli, rotations.shape[1])

    def set_visible(self, visibles):
        self.visible = visibles
        self.num_stimuli = max(self.num_stimuli, visibles.shape[0])

    def set_target(self, targets):
        self.target = targets
        self.num_stimuli = max(self.num_stimuli, targets.shape[0])

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
                    "sizeTHREEJS": self.size.tolist(),
                    "positionTHREEJS": {"x": self.position[0].tolist(),
                                 "y": self.position[1].tolist(),
                                 "z": self.position[2].tolist()},
                    "rotationDegrees": {"x": self.rotation[0].tolist(),
                                 "y": self.rotation[1].tolist(),
                                 "z": self.rotation[2].tolist()},
                    "visible": self.visible.tolist(),
                    "target": self.target.tolist()}
        return obj_dict
    
    def from_dict(obj_dict):
        meshpath = obj_dict["meshpath"]
        objectdoc = obj_dict["objectdoc"]
        texture = obj_dict["texture"]
        material_type = obj_dict["material"]["type"]
        material_color = obj_dict["material"]["color"]
        material_metalness = obj_dict["material"]["metalness"]
        material_roughness = obj_dict["material"]["roughness"]
        material_reflectivity = obj_dict["material"]["reflectivity"]
        material_opacity = obj_dict["material"]["opacity"][0]
        material_transparent = obj_dict["material"]["transparent"]
        sizes = obj_dict["sizeTHREEJS"]
        positions = [obj_dict["positionTHREEJS"]["x"],
                     obj_dict["positionTHREEJS"]["y"],
                     obj_dict["positionTHREEJS"]["z"]]
        rotations = [obj_dict["rotationDegrees"]["x"],
                     obj_dict["rotationDegrees"]["y"],
                     obj_dict["rotationDegrees"]["z"]]
        visibles = obj_dict["visible"]
        targets = obj_dict["target"]
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
        sizes = np.array(sizes)
        positions = np.array(positions)
        rotations = np.array(rotations)
        visibles = np.array(visibles)
        targets = np.array(targets)
        object = Object(meshpath, objectdoc, texture,
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

    def __init__(self, 
                 imagebag="/mkturkfiles/assets/polyhaven/",
                 imageidx=5,
                 visible=1,
                 img_size=10):
        self.imagebag = imagebag
        self.imageidx = imageidx
        self.visible = visible
        self.size = img_size

    def to_dict(self):
        img_dict = {"imagebag": self.imagebag,
                    "imageidx": [self.imageidx],
                    "visible": [self.visible],
                    "sizeTHREEJS": [self.size]}
        return img_dict
    
    def from_dict(img_dict):
        imagebag = img_dict["imagebag"]
        imageidx = img_dict["imageidx"][0]
        visible = img_dict["visible"][0]
        img_size = img_dict["sizeTHREEJS"][0]
        img = Image(imagebag, imageidx,
                       visible, img_size)
        return img

class Filters:

    def __init__(self):
        self.blur = []
        self.brightness = []
        self.contrast = []
        self.grayscale = []
        self.huerotate = []
        self.invert = []
        self.opacity = []
        self.saturate = []
        self.sepia = []

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
    
    def from_dict(filter_dict):
        blur = filter_dict["blur"]
        brightness = filter_dict["brightness"]
        contrast = filter_dict["contrast"]
        grayscale = filter_dict["grayscale"]
        huerotate = filter_dict["huerotate"]
        invert = filter_dict["invert"]
        opacity = filter_dict["opacity"]
        saturate = filter_dict["saturate"]
        sepia = filter_dict["sepia"]
        filters = Filters()
        return filters


class Scenefile:

    def __init__(self):
        self.camera = None
        self.dir_light = None
        self.amb_light = None
        self.obj0 = None
        self.obj1 = None
        self.obj2 = None
        self.img = None
        self.obj_filters = None
        self.img_filters = None
        self.duration = 0
        return

    def from_json(json_path):

        scenefile = Scenefile()

        with open(json_path, "r") as sf:
            scene_dict = json.load(sf)

        cam_dict = scene_dict["CAMERAS"]
        scenefile.camera = Camera.from_dict(cam_dict["camera00"])

        light_dict = scene_dict["LIGHTS"]
        scenefile.dir_light = Light.from_dict(light_dict["light00"])
        scenefile.amb_light = Light.from_dict(light_dict["light01"])

        obj_dict = scene_dict["OBJECTS"]
        scenefile.obj0 = Object.from_dict(obj_dict["obj0"])
        scenefile.obj1 = Object.from_dict(obj_dict["obj1"])
        scenefile.obj2 = Object.from_dict(obj_dict["obj2"])

        img_dict = scene_dict["IMAGES"]
        scenefile.img = Image.from_dict(img_dict)

        obj_filter_dict = scene_dict["OBJECTFILTERS"]
        scenefile.obj_filters = Filters.from_dict(obj_filter_dict)

        img_filter_dict = scene_dict["IMAGEFILTERS"]
        scenefile.img_filters = Filters.from_dict(img_filter_dict)

        scenefile.duration = scene_dict["durationMS"]

        return scenefile

    def to_json(self, json_path):

        scene_dict = {"CAMERAS": None, "LIGHTS": None, 
                      "OBJECTS": None, "IMAGES": None,
                      "OBJECTFILTERS": None,
                      "IMAGEFILTERS": None,
                      "durationMS": 0}

        scene_dict["CAMERAS"] = {"camera00": None}
        scene_dict["CAMERAS"]["camera00"] = self.camera.to_dict()

        scene_dict["LIGHTS"] = {"light00": None, "light01": None}
        scene_dict["LIGHTS"]["light00"] = self.dir_light.to_dict()
        scene_dict["LIGHTS"]["light01"] = self.amb_light.to_dict()

        scene_dict["OBJECTS"] = {"obj0": None, "obj1": None, "obj2": None}
        scene_dict["OBJECTS"]["obj0"] = self.obj0.to_dict()
        scene_dict["OBJECTS"]["obj1"] = self.obj1.to_dict()
        scene_dict["OBJECTS"]["obj2"] = self.obj2.to_dict()

        scene_dict["IMAGES"] = self.img.to_dict()

        scene_dict["OBJECTFILTERS"] = self.obj_filters.to_dict()
        scene_dict["IMAGEFILTERS"] = self.img_filters.to_dict()

        scene_dict["durationMS"] = self.duration

        with open(json_path, "w") as outfile:
            json.dump(scene_dict, outfile)
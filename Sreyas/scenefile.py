import os
import json
import numpy as np

#TODO: Add the ability to include arbitrarily many objects, cameras, lights
#TODO: Add the ability to animate filter params, background indices.
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

    def is_consistent(self):
        return self.position.shape[1] == self.target.shape[1] == self.num_stimuli
    
    def duplicate(self, factor):
        self.set_position(np.repeat(self.position, factor, axis=1))
        self.set_target(np.repeat(self.target, factor, axis=1))

    def copy(self):
        cam = Camera(self.camera_type, self.field_of_view,
                     self.near, self.far, self.visible)
        cam.set_position(self.position.copy())
        cam.set_target(self.target.copy())
        return cam

    def subset(self, i, j):
        assert i <= j and i >= 0 and j <= self.num_stimuli, "Improper indices for subset, please try again!"
        sub_cam = Camera(self.camera_type, self.field_of_view,
                         self.near, self.far)
        sub_cam.set_position(self.position[:,i:j+1])
        sub_cam.set_target(self.target[:,i:j+1])
        return sub_cam

    def concatenate(cam1, cam2):
        assert cam1.is_consistent() and cam2.is_consistent()
        assert cam1.camera_type == cam2.camera_type
        assert cam1.field_of_view == cam2.field_of_view
        assert cam1.near == cam2.near
        assert cam1.far == cam2.far
        assert cam1.visible == cam2.visible
        cam = Camera(cam1.camera_type, 
                     cam1.field_of_view, 
                     cam1.near, cam1.far, 
                     cam1.visible)
        cam.set_position(np.concatenate((cam1.position, cam2.position), axis=1))
        cam.set_target(np.concatenate((cam1.target, cam2.target), axis=1))
        return cam

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

    def is_consistent(self):
        return self.position.shape[1] == self.num_stimuli
    
    def duplicate(self, factor):
        self.set_position(np.repeat(self.position, factor, axis=1))

    def copy(self):
        light = Light(self.light_type, self.color,
                         self.intensity, self.visible)
        light.set_position(self.position.copy())
        return light

    def subset(self, i, j):
        assert i <= j and i >= 0 and j <= self.num_stimuli, "Improper indices for subset, please try again!"
        sub_light = Light(self.light_type, self.color,
                         self.intensity, self.visible)
        sub_light.set_position(self.position[:,i:j+1])
        return sub_light

    def concatenate(light1, light2):
        assert light1.is_consistent() and light2.is_consistent(), "Lights not consistent!"
        assert light1.light_type == light2.light_type
        assert light1.color == light2.color
        assert light1.intensity == light2.intensity
        assert light1.visible == light2.visible
        light = Camera(light1.light_type, 
                     light1.color, 
                     light1.intensity, 
                     light1.visible)
        light.set_position(np.concatenate((light1.position, light2.position), axis=1))
        return light

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

    def is_consistent(self):
        return self.position.shape[1] == self.rotation.shape[1] \
            == self.visible.shape[0] == self.target.shape[0]
    
    def duplicate(self, factor):
        self.set_size(np.repeat(self.size, factor))
        self.set_position(np.repeat(self.position, factor, axis=1))
        self.set_rotation(np.repeat(self.rotation, factor, axis=1))
        self.set_visible(np.repeat(self.visible, factor))
        self.set_target(np.repeat(self.target, factor))

    def copy(self):
        obj = Object(self.meshpath, self.objectdoc,
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
        sub_obj = Object(self.meshpath, self.objectdoc,
                         self.texture, self.material_type,
                         self.material_color, self.material_metalness,
                         self.material_roughness, self.material_reflectivity,
                         self.material_opacity, self.material_transparent)
        sub_obj.set_size(self.size[i:j+1])
        sub_obj.set_position(self.position[:,i:j+1])
        sub_obj.set_rotation(self.rotation[:,i:j+1])
        sub_obj.set_visible(self.visible[i:j+1])
        sub_obj.set_target(self.target[i:j+1])
        return sub_obj

    def concatenate(o1, o2):
        assert o1.is_consistent() and o2.is_consistent()
        assert o1.meshpath == o2.meshpath
        assert o1.objectdoc == o2.objectdoc
        assert o1.texture == o2.texture
        assert o1.material_type == o2.material_type
        assert o1.material_color == o2.material_color
        assert o1.material_metalness == o2.material_metalness
        assert o1.material_roughness == o2.material_roughness
        assert o1.material_reflectivity == o2.material_reflectivity
        assert o1.material_opacity == o2.material_opacity
        assert o1.material_transparent == o2.material_transparent
        obj = Object(o1.meshpath, o1.objectdoc, o1.texture,
                     o1.material_type, o1.material_color,
                     o1.material_metalness,
                     o1.material_roughness, 
                     o1.material_reflectivity,
                     o1.material_opacity,
                     o1.material_transparent)
        obj.set_size(np.concatenate((o1.size, o2.size)))
        obj.set_position(np.concatenate((o1.position, o2.position), axis=1))
        obj.set_rotation(np.concatenate((o1.rotation, o2.rotation), axis=1))
        obj.set_visible(np.concatenate((o1.visible, o2.visible)))
        obj.set_target(np.concatenate((o1.target, o2.target)))
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
        self.num_stimuli = -1

    def is_consistent(self):
        return True
    
    def duplicate(self, factor):
        return

    def copy(self):
        img = Image(self.imagebag, self.imageidx, self.visible, self.size)
        return img

    def subset(self, i, j):
        return self.copy()
    
    def concatenate(img1, img2):
        assert img1.is_consistent() and img2.is_consistent()
        assert img1.imagebag == img2.imagebag
        assert img1.imageidx == img2.imageidx
        assert img1.visible == img2.visible
        assert img1.size == img2.size
        img = Image(img1.imagebag, 
                     img1.imageidx, 
                     img1.visible, 
                     img1.size)
        return img

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
        self.num_stimuli = -1

    def is_consistent(self):
        return True
    
    def duplicate(self, factor):
        return
    
    def copy(self):
        return Filters()
    
    def subset(self, i, j):
        return self.copy()
    
    def concatenate(filter1, filter2):
        assert filter1.is_consistent() and filter2.is_consistent()
        filter = Filters()
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


class Animation:

    animable_params = ["cam:pos", "dir_light:pos", "amb_light:pos",
                       "obj0:size", "obj0:pos", "obj0:rot",
                       "obj1:size", "obj1:pos", "obj1:rot",
                       "obj2:size", "obj2:pos", "obj2:rot"]

    def __init__(self, param, range):
        self.param = param
        assert param in Animation.animable_params, "Specified param not recognized, please try again!"
        self.range = range
        if param[-3:] == "pos" or param[-3:] == "rot":
            self.num_stimuli = range.shape[1]
        else: self.num_stimuli = range.shape[0]


class Scenefile:

    def __init__(self, camera=None, dir_light=None, amb_light=None,
                 obj0=None, obj1=None, obj2=None, img=None,
                 obj_filters=None, img_filters=None, num_stimuli=0,
                 duration=100):
        self.camera = Camera() if (camera is None) else camera
        self.dir_light = Light("DirectionalLight") if (dir_light is None) else dir_light
        self.amb_light = Light("AmbientLight") if (amb_light is None) else amb_light
        self.obj0 = Object(None) if (obj0 is None) else obj0
        self.obj1 = Object(None) if (obj1 is None) else obj1
        self.obj2 = Object(None) if (obj2 is None) else obj2
        self.img = Image() if (img is None) else img
        self.obj_filters = Filters() if (obj_filters is None) else obj_filters
        self.img_filters = Filters() if (img_filters is None) else img_filters
        self.num_stimuli = num_stimuli
        self.duration = duration
    
    def get_elements(self):
        return self.camera, self.dir_light, self.amb_light, \
            self.obj0, self.obj1, self.obj2, \
            self.img, self.obj_filters, self.img_filters

    def is_consistent(self):
        flag = True
        for scene_element in self.get_elements():
            elt_flag = (scene_element.num_stimuli == -1) or (scene_element.num_stimuli == self.num_stimuli)
            flag = flag and elt_flag
            if not flag: print(f"Consistency broken by {scene_element}!")
        return flag
    
    def duplicate(self, factor):
        self.camera.duplicate(factor)
        self.dir_light.duplicate(factor)
        self.amb_light.duplicate(factor)
        self.obj0.duplicate(factor)
        self.obj1.duplicate(factor)
        self.obj2.duplicate(factor)
        self.img.duplicate(factor)
        self.obj_filters.duplicate(factor)
        self.img_filters.duplicate(factor)
        self.num_stimuli *= factor
        assert self.is_consistent()

    def copy(self):
        cam = self.camera.copy()
        dir_light = self.dir_light.copy()
        amb_light = self.amb_light.copy()
        obj0 = self.obj0.copy()
        obj1 = self.obj1.copy()
        obj2 = self.obj2.copy()
        img = self.img.copy()
        obj_filters = self.obj_filters.copy()
        img_filters = self.img_filters.copy()
        scenefile = Scenefile(cam, dir_light, amb_light,
                                  obj0, obj1, obj2,
                                  img, obj_filters, img_filters,
                                  self.num_stimuli, self.duration)
        return scenefile
    
    def subset(self, i, j):
        assert i <= j and i >= 0 and j <= self.num_stimuli, "Improper indices for subset, please try again!"
        sub_cam = self.camera.subset(i, j)
        sub_dir_light = self.dir_light.subset(i, j)
        sub_amb_light = self.amb_light.subset(i, j)
        sub_obj0 = self.obj0.subset(i, j)
        sub_obj1 = self.obj1.subset(i, j)
        sub_obj2 = self.obj2.subset(i, j)
        sub_img = self.img.subset(i, j)
        sub_obj_filters = self.obj_filters.subset(i, j)
        sub_img_filters = self.img_filters.subset(i, j)
        sub_scenefile = Scenefile(sub_cam, sub_dir_light, sub_amb_light,
                                  sub_obj0, sub_obj1, sub_obj2,
                                  sub_img, sub_obj_filters, sub_img_filters,
                                  j - i + 1, self.duration)
        assert sub_scenefile.is_consistent(), "Subset scenefile is not consistent!"
        return sub_scenefile
    
    def concatenate(scenefile1, scenefile2):
        assert scenefile1.is_consistent() and scenefile2.is_consistent()
        assert scenefile1.duration == scenefile2.duration, "Durations must match for concatenation!"
        cam = Camera.concatenate(scenefile1.camera, scenefile2.camera)
        dir_light = Light.concatenate(scenefile1.dir_light, scenefile2.dir_light)
        amb_light = Light.concatenate(scenefile1.amb_light, scenefile2.amb_light)
        obj0 = Object.concatenate(scenefile1.obj0, scenefile2.obj0)
        obj1 = Object.concatenate(scenefile1.obj1, scenefile2.obj1)
        obj2 = Object.concatenate(scenefile1.obj2, scenefile2.obj2)
        img = Image.concatenate(scenefile1.img, scenefile2.img)
        obj_filters = Filters.concatenate(scenefile1.obj_filters, scenefile2.obj_filters)
        img_filters = Filters.concatenate(scenefile1.img_filters, scenefile2.img_filters)
        scenefile = Scenefile(cam, dir_light, amb_light,
                              obj0, obj1, obj2,
                              img, obj_filters, img_filters,
                              scenefile1.num_stimuli + scenefile2.num_stimuli, 
                              scenefile1.duration)
        assert scenefile.is_consistent(), "Concatenated scenefile not consistent!"
        return scenefile

    def from_json(json_path):

        print(f"Loading scenefile from {json_path}!")

        scenefile = Scenefile()

        with open(json_path, "r") as sf:
            scene_dict = json.load(sf)

        num_stimuli = 0

        print("Loading camera!")
        cam_dict = scene_dict["CAMERAS"]
        scenefile.camera = Camera.from_dict(cam_dict["camera00"])
        assert scenefile.camera.is_consistent(), "Camera not consistent!"
        num_stimuli = max(num_stimuli, scenefile.camera.num_stimuli)
        print(f"Camera loading done. Number of stimuli at {num_stimuli}.")

        print("Loading lights!")
        light_dict = scene_dict["LIGHTS"]
        scenefile.dir_light = Light.from_dict(light_dict["light00"])
        scenefile.amb_light = Light.from_dict(light_dict["light01"])
        assert scenefile.dir_light.is_consistent(), "Directional light not consistent!"
        assert scenefile.amb_light.is_consistent(), "Ambient light not consistent!"
        num_stimuli = max(num_stimuli, scenefile.dir_light.num_stimuli, scenefile.amb_light.num_stimuli)
        print(f"Light loading done. Number of stimuli at {num_stimuli}.")

        print("Loading objects!")
        obj_dict = scene_dict["OBJECTS"]
        scenefile.obj0 = Object.from_dict(obj_dict["obj0"])
        scenefile.obj1 = Object.from_dict(obj_dict["obj1"])
        scenefile.obj2 = Object.from_dict(obj_dict["obj2"])
        assert scenefile.obj0.is_consistent(), "Object 0 not consistent!"
        assert scenefile.obj1.is_consistent(), "Object 1 not consistent!"
        assert scenefile.obj2.is_consistent(), "Object 2 not consistent!"
        num_stimuli = max(num_stimuli, scenefile.obj0.num_stimuli,
                          scenefile.obj1.num_stimuli, 
                          scenefile.obj2.num_stimuli)
        print(f"Object loading done. Number of stimuli at {num_stimuli}.")

        print("Loading images!")
        img_dict = scene_dict["IMAGES"]
        scenefile.img = Image.from_dict(img_dict)
        assert scenefile.img.is_consistent(), "Images not consistent!"
        print(f"Images done. Number of stimuli at {num_stimuli}.")

        print("Loading object filters!")
        obj_filter_dict = scene_dict["OBJECTFILTERS"]
        scenefile.obj_filters = Filters.from_dict(obj_filter_dict)
        assert scenefile.obj_filters.is_consistent(), "Object filters not consistent!"
        print(f"Object filter loading done. Number of stimuli at {num_stimuli}.")
    
        print("Loading image filters!")
        img_filter_dict = scene_dict["IMAGEFILTERS"]
        scenefile.img_filters = Filters.from_dict(img_filter_dict)
        assert scenefile.img_filters.is_consistent(), "Image filters not consistent!"
        print(f"Image filter loading done. Number of stimuli at {num_stimuli}.")

        scenefile.num_stimuli = num_stimuli

        for scene_element in scenefile.get_elements():
            if scene_element.num_stimuli != -1:
                if scene_element.num_stimuli == 1:
                    scene_element.duplicate(num_stimuli)
                else: assert scene_element.num_stimuli == scenefile.num_stimuli

        assert scenefile.is_consistent(), "Scenefile not consistent! Please try again."

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

    # TODO: Ensure num_stimuli is uniform before this is done
    # TODO: Assign scene elements IDs 
    def apply_anim(scene, animation, base):
        assert scene.is_consistent()
        add_scene = base.copy()
        add_scene.duplicate(animation.num_stimuli)
        ["cam:pos", "dir_light:pos", 
                       "obj0:size", "obj0:pos", "obj0:rot",
                       "obj1:size", "obj1:pos", "obj1:rot",
                       "obj2:size", "obj2:pos", "obj2:rot"]
        match animation.param:
            case "cam:pos":
                add_scene.camera.set_position(animation.range)
            case "dir_light:pos":
                add_scene.dir_light.set_position(animation.range)
            case "amb_light:pos":
                add_scene.amb_light.set_position(animation.range)
            case "obj0:size":
                add_scene.obj0.set_size(animation.range)
            case "obj0:pos":
                add_scene.obj0.set_position(animation.range)
            case "obj0:rot":
                add_scene.obj0.set_rotation(animation.range)
            case "obj1:size":
                add_scene.obj1.set_size(animation.range)
            case "obj1:pos":
                add_scene.obj1.set_position(animation.range)
            case "obj1:rot":
                add_scene.obj1.set_rotation(animation.range)
            case "obj2:size":
                add_scene.obj2.set_size(animation.range)
            case "obj2:pos":
                add_scene.obj2.set_position(animation.range)
            case "obj2:rot":
                add_scene.obj2.set_rotation(animation.range)
            case _:
                raise ValueError(f"Parameter not one of the following animatable params: {Animation.animable_params}. Please try again.")
        return Scenefile.concatenate(scene, add_scene)


class ScenefileSchema:

    def __init__(self, base, animations=[]):
        self.base = base
        assert self.base.num_stimuli == 1
        self.anims = animations
        self.num_anims = len(self.anims)

    def add_anim(self, animations):
        self.anims += animations
        self.num_anims += len(animations)

    def generate_scenefile(self):
        scenefile = self.base.copy()
        for anim in self.anims:
            scenefile = Scenefile.apply_anim(scenefile, anim, self.base)
        return scenefile
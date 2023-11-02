import json
import numpy as np

#TODO: Add the ability to include arbitrarily many objects, cameras, lights
#TODO: Add the ability to animate filter params, background indices.
#TODO: Add flags to accurately maintain the number of stimuli within and across scene elements.
#TODO: Abstract the logic of scene element into a separate class.
#TODO: Include ability to save out scenefile to JSON.
#TODO: Change np arrays to Python lists to enable animation of movies.

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
        self.position = np.zeros((3, self.num_stimuli))
        self.target = np.zeros((3, self.num_stimuli))
        self.visible = visible

    def set_position(self, position):
        assert len(position.shape) == 2 and position.shape[0] == 3, "Position must be of shape (3, num_stimuli)!"
        self.position = position
        self.num_stimuli = max(self.num_stimuli, position.shape[1])
    
    def set_target(self, target):
        assert len(target.shape) == 2 and target.shape[0] == 3, "Target must be of shape (3, num_stimuli)!"
        self.target = target
        self.num_stimuli = max(self.num_stimuli, target.shape[1])

    def is_consistent(self):
        return self.position.shape[1] == self.target.shape[1] == self.num_stimuli
    
    def duplicate(self, factor):
        self.set_position(np.repeat(self.position, factor, axis=1))
        self.set_target(np.repeat(self.target, factor, axis=1))

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
        sub_cam.set_position(self.position[:,i:j+1])
        sub_cam.set_target(self.target[:,i:j+1])
        return sub_cam

    def concatenate(cls, cam1, cam2):
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
    
    def from_dict(cam_dict, name):
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
        camera = Camera(name, camera_type,
                        field_of_view,
                        near, far,
                        visible)
        camera.set_position(position)
        camera.set_target(target)
        return camera
    
class Light:

    def __init__(self, name="light", light_type="DirectionalLight", color=0xffffff, intensity=5, visible=1):
        self.name = name
        self.light_type = light_type
        self.color = color
        self.intensity = intensity
        self.visible = visible
        self.num_stimuli = 1
        self.position = np.zeros((3, self.num_stimuli))

    def set_position(self, position):
        assert len(position.shape) == 2 and position.shape[0] == 3, "Position must be of shape (3, num_stimuli)!"
        self.position = position
        self.num_stimuli = max(self.num_stimuli, position.shape[1])

    def is_consistent(self):
        return self.position.shape[1] == self.num_stimuli
    
    def duplicate(self, factor):
        self.set_position(np.repeat(self.position, factor, axis=1))

    def copy(self):
        light = Light(self.name, self.light_type, self.color,
                         self.intensity, self.visible)
        light.set_position(self.position.copy())
        return light

    def subset(self, i, j):
        assert i <= j and i >= 0 and j <= self.num_stimuli, "Improper indices for subset, please try again!"
        sub_light = Light(self.name, self.light_type, self.color,
                         self.intensity, self.visible)
        sub_light.set_position(self.position[:,i:j+1])
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
    
    def from_dict(light_dict, name):
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
        light = Light(name, light_type, color, intensity, visible)
        light.set_position(position)
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
        self.size = np.zeros(self.num_stimuli)
        self.position = np.zeros((3, self.num_stimuli))
        self.rotation = np.zeros((3, self.num_stimuli))
        self.visible = np.zeros(self.num_stimuli, dtype="int")
        self.target = np.zeros(self.num_stimuli, dtype="int")

    def set_size(self, sizes):
        self.size = sizes
        self.num_stimuli = max(self.num_stimuli, sizes.shape[0])

    def set_position(self, position):
        assert len(position.shape) == 2 and position.shape[0] == 3, "Position must be of shape (3, num_stimuli)!"
        self.position = position
        self.num_stimuli = max(self.num_stimuli, position.shape[1])

    def set_rotation(self, rotation):
        assert len(rotation.shape) == 2 and rotation.shape[0] == 3, "Rotation must be of shape (3, num_stimuli)!"
        self.rotation = rotation
        self.num_stimuli = max(self.num_stimuli, rotation.shape[1])

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
        sub_obj.set_position(self.position[:,i:j+1])
        sub_obj.set_rotation(self.rotation[:,i:j+1])
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
    
    def from_dict(obj_dict, name):
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
        assert img1.is_consistent() and img2.is_consistent(), "Images must be consistent to concatenate!"
        assert img1.imagebag == img2.imagebag, "Imagebags must match!"
        assert img1.imageidx == img2.imageidx, "Image indices must match!"
        assert img1.visible == img2.visible, "Image visibles must match!"
        assert img1.size == img2.size, "Image sizes must match!"
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
        if "visible" in img_dict.keys() and len(img_dict["visible"]) > 0:
            visible = img_dict["visible"][0]
        else:
            print("Adding visible flag to background. Setting to 1.")
            visible = 1
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
        assert filter1.is_consistent() and filter2.is_consistent(), "Filters must be consistent to concatenate!"
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

    animable_params = ["cam:pos", "light:pos", "obj:size", "obj:pos", "obj:rot"]

    def __init__(self, param, range, element_name):
        self.param = param
        assert param in Animation.animable_params, "Specified param not recognized, please try again!"
        self.range = range
        if param[-3:] == "pos" or param[-3:] == "rot":
            self.num_stimuli = range.shape[1]
        else: self.num_stimuli = range.shape[0]
        self.element_name = element_name


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

    def is_consistent(self):
        print("Initiating scenefile consistency check.")
        flag = True
        names = []
        print("Names", names)
        for scene_element in self.get_elements():
            if scene_element.num_stimuli != -1:
                print("elt name", scene_element.name)
            name_flag = (scene_element.num_stimuli == -1 or (not (scene_element.name in names)))
            if not name_flag: print("Name", names)
            if scene_element.num_stimuli != -1 and name_flag: names.append(scene_element.name)
            elt_flag = (scene_element.num_stimuli == -1) or (scene_element.num_stimuli == self.num_stimuli)
            flag = flag and elt_flag and name_flag and scene_element.is_consistent()
            if not flag: print(f"Consistency broken by {scene_element}!", name_flag, elt_flag, flag)
        names = []
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
        cam = self.camera.copy()
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

    def from_json(json_path):

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

        print(scenefile.get_elements())
        assert scenefile.is_consistent(), "Scenefile not consistent! Please try again."

        scenefile.duration = scene_dict["durationMS"]

        return scenefile

    def to_json(self, json_path):

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
            json.dump(scene_dict, outfile)

    def apply_anim(scene, animation, base):
        assert scene.is_consistent(), "Scene must be consistent to animate!"
        add_scene = base.copy()
        add_scene.duplicate(animation.num_stimuli)
        match animation.param:
            case "cam:pos":
                cam = add_scene.get_camera(animation.element_name)
                assert cam is not None, "Camera not found!"
                cam.set_position(animation.range)
            case "light:pos":
                light = add_scene.get_light(animation.element_name)
                assert light is not None, "Light not found!"
                light.set_position(animation.range)
            case "obj:size":
                obj = add_scene.get_object(animation.element_name)
                assert obj is not None, "Object not found!"
                obj.set_size(animation.range)
            case "obj:pos":
                obj = add_scene.get_object(animation.element_name)
                assert obj is not None, "Object not found!"
                obj.set_position(animation.range)
            case "obj:rot":
                obj = add_scene.get_object(animation.element_name)
                assert obj is not None, "Object not found!"
                obj.set_rotation(animation.range)
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
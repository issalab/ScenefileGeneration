import os
import json
import numpy as np

mkfiles_path = "gs://sandbox-ce2c5.appspot.com/mkturkfiles"

object_mesh_paths = ["/mkturkfiles/assets/objaverse_final/ambulance/41574a23a9ae4c9d990ffe672af6281e.glb",
                     "/mkturkfiles/assets/objaverse_final/ambulance/41574a23a9ae4c9d990ffe672af6281e.glb",
                     "/mkturkfiles/assets/objaverse_final/ambulance/41574a23a9ae4c9d990ffe672af6281e.glb",
                     "/mkturkfiles/assets/objaverse_final/ambulance/41574a23a9ae4c9d990ffe672af6281e.glb",
                     "/mkturkfiles/assets/objaverse_final/ambulance/41574a23a9ae4c9d990ffe672af6281e.glb",
                     "/mkturkfiles/assets/objaverse_final/ambulance/41574a23a9ae4c9d990ffe672af6281e.glb"]

bkg_idxs = [1, 19]

condition_ids = ["1X", "1A", "1BC", "1ABC", "0ABC", "2DEF"]

# TODO: add different meshes for A-F
condition_info = {
    "1X": {
        "id": 0,
        "num_stimuli": 27,
        "bkgd": 0,
        "obj_meshes": [0, 0, 0],
        "obj_visible": [0, 0, 0],
        "obj_anim": -1
    },
    "1A": {
        "id": 1,
        "num_stimuli": 39,
        "bkgd": 0,
        "obj_meshes": [0, 1, 2],
        "obj_visible": [1, 0, 0],
        "obj_anim": 0
    },
    "1BC": {
        "id": 2,
        "num_stimuli": 39,
        "bkgd": 0,
        "obj_meshes": [0, 1, 2],
        "obj_visible": [0, 1, 1],
        "obj_anim": 1
    },
    "1ABC": {
        "id": 3,
        "num_stimuli": 39,
        "bkgd": 0,
        "obj_meshes": [0, 1, 2],
        "obj_visible": [1, 1, 1],
        "obj_anim": 0
    },
    "0ABC": {
        "id": 4,
        "num_stimuli": 39,
        "bkgd": -1,
        "obj_meshes": [0, 1, 2],
        "obj_visible": [1, 1, 1],
        "obj_anim": 1
    },
    "2DEF": {
        "id": 5,
        "num_stimuli": 39,
        "bkgd": 1,
        "obj_meshes": [3, 4, 5],
        "obj_visible": [1, 1, 1],
        "obj_anim": 1
    } 
}

def generate_hexagon(r):
    angles = np.linspace(0, 2*np.pi, num=6, endpoint=False)
    xs = [0]*6
    zs = [0]*6
    for i in range(6):
        xs[i] = r * np.cos(angles[i])
        zs[i] = r * np.sin(angles[i])
    return xs, zs

def to_radians(theta): return theta*np.pi/180

def camera_rotate(theta, base_length):
    return base_length*np.tan(to_radians(theta))

class SceneFileGenerator():

    cam_fov = 45
    room_dim = 200

    def __init__(self, cam_offset_z = 22,
                 cam_offset_y = 0, obj_size = 11,
                 obj_disp = 9, light_height = 20,
                 hexagon_rad = 0):
        self.cam_offset_z = cam_offset_z
        self.cam_dist = SceneFileGenerator.room_dim/2 - cam_offset_z
        self.cam_offset_y = cam_offset_y
        self.obj_size = obj_size
        self.obj_disp = obj_disp
        self.light_height = light_height
        self.hexagon_rad = hexagon_rad
        if self.hexagon_rad == 0:
            self.hexagon_rad = self.cam_dist

    def compute_object_positions(self):
        return [[0, self.obj_disp],
                [-self.obj_disp*np.sqrt(3)/2, -self.obj_disp/2],
                [self.obj_disp*np.sqrt(3)/2, -self.obj_disp/2]]

    def load_empty_scene_dict(self):
        with open("neural0_empty_scenefile.json", "r") as sf:
            scene_dict = json.load(sf)
        return scene_dict

    def extract_scene_subdicts(self, scene_dict):
        return scene_dict["CAMERAS"]["camera00"],\
            scene_dict["LIGHTS"]["light00"], \
            scene_dict["LIGHTS"]["light01"], \
            scene_dict["OBJECTS"]["obj0"], \
            scene_dict["OBJECTS"]["obj1"], \
            scene_dict["OBJECTS"]["obj2"], \
            scene_dict["IMAGES"], \
            scene_dict["OBJECTFILTERS"], \
            scene_dict["IMAGEFILTERS"]

    def get_scene_subdicts(self, scene_dict):
        camera_dict, dir_light_dict, _, \
        obj0_dict, obj1_dict, obj2_dict, \
        images_dict, object_filters_dict, \
        image_filters_dict = self.extract_scene_subdicts(scene_dict)

        return {"cam": camera_dict, "light": dir_light_dict,
                "obj": [obj0_dict, obj1_dict, obj2_dict],
                "img": images_dict,
                "filters": {"obj": object_filters_dict, "img": image_filters_dict}}

    def prime_scene_subdicts(self, scene_subdicts, condition):
        num_stimuli = condition_info[condition]["num_stimuli"]
        for i in range(3):
            scene_subdicts["obj"][i]["meshpath"] = \
                object_mesh_paths[condition_info[condition]["obj_meshes"][i]]
            scene_subdicts["obj"][i]["visible"] = \
                [condition_info[condition]["obj_visible"][i]]
        if condition_info[condition]["bkgd"] == -1:
            scene_subdicts["img"]["imageidx"] = []
        else:
            scene_subdicts["img"]["imageidx"] = [condition_info[condition]["bkgd"]]

        # Camera x, z, x rotation AND hexagonal positions
        scene_subdicts["cam"]["position"]["x"] = [0]*num_stimuli
        scene_subdicts["cam"]["position"]["y"] = [self.cam_offset_y]
        scene_subdicts["cam"]["position"]["z"] = [self.cam_dist]*num_stimuli
        scene_subdicts["cam"]["targetTHREEJS"]["x"] = [0]*num_stimuli
        
        object_pos = self.compute_object_positions()
        for i in range(3):
            scene_subdicts["obj"][i]["sizeTHREEJS"] = [self.obj_size]
            scene_subdicts["obj"][i]["positionTHREEJS"]["y"] = [self.obj_disp]

            # Object x, z, x rotation
            scene_subdicts["obj"][i]["positionTHREEJS"]["x"] = [object_pos[i][0]]*num_stimuli
            scene_subdicts["obj"][i]["positionTHREEJS"]["y"] = [object_pos[i][1]]
            scene_subdicts["obj"][i]["positionTHREEJS"]["z"] = [0]*num_stimuli
            scene_subdicts["obj"][i]["rotationDegrees"]["y"] = [object_pos[i][1]]*num_stimuli

        # Light direction
        scene_subdicts["light"]["position"]["y"] = [self.light_height]*num_stimuli

        # Hue rotation
        scene_subdicts["filters"]["obj"]["huerotate"] = [0]*num_stimuli
        scene_subdicts["filters"]["img"]["huerotate"] = [0]*num_stimuli

    def populate_scene_subdicts(self, scene_subdicts, condition):
        # TODO: Tweak parameters to appropriate ranges
        # Keep running stim index
        stim_idx = 0
        # Populate camera stimuli (theta_x, x, z)
        # Maintain index 0 as base
        stim_idx += 1
        scene_subdicts["cam"]["targetTHREEJS"]["x"][stim_idx:stim_idx+4] = [camera_rotate(t, self.cam_dist) for t in [-30, -15, 15, 30]]
        scene_subdicts["cam"]["targetTHREEJS"]["x"][stim_idx:stim_idx+4] = [camera_rotate(t, self.cam_dist) for t in [-15, -7.5, 7.5, 15]]
        stim_idx += 4
        scene_subdicts["cam"]["position"]["x"][stim_idx:stim_idx+4] = [k*self.obj_size for k in [-8, -4, 4, 8]]
        stim_idx += 4
        scene_subdicts["cam"]["position"]["z"][stim_idx:stim_idx+4] = [self.cam_dist + k*self.obj_size for k in [-6, -3, 3, 6]]
        stim_idx += 4
        # Populate hexagon
        scene_subdicts["cam"]["position"]["x"][stim_idx:stim_idx+6], \
            scene_subdicts["cam"]["position"]["z"][stim_idx:stim_idx+6] = \
            generate_hexagon(self.cam_dist)
        stim_idx += 6
        # If object anim, populate object anim (theta_x, x, z)
        if condition_info[condition]["obj_anim"] != -1:
            a = condition_info[condition]["obj_anim"]
            scene_subdicts["obj"][a]["rotationDegrees"]["y"][stim_idx:stim_idx+4] = [-60, -30, 30, 60]
            stim_idx += 4
            scene_subdicts["obj"][a]["positionTHREEJS"]["x"][stim_idx:stim_idx+4] = [k*self.obj_size for k in [-2, -1, 1, 2]]
            stim_idx += 4
            scene_subdicts["obj"][a]["positionTHREEJS"]["z"][stim_idx:stim_idx+4] = [k*self.obj_size for k in [-6, -3, 3, 6]]
            stim_idx += 4
        # Populate light (x?)
        scene_subdicts["light"]["position"]["y"][stim_idx:stim_idx+4] = [k*self.obj_size for k in [-8, -4, 4, 8]]
        stim_idx += 4
        # Populate hue (theta)
        scene_subdicts["filters"]["obj"]["huerotate"][stim_idx:stim_idx+4] = [-120, -60, 60, 120]
        scene_subdicts["filters"]["img"]["huerotate"][stim_idx:stim_idx+4] = [-120, -60, 60, 120]
        stim_idx += 4 
        assert stim_idx == condition_info[condition]["num_stimuli"]

    def save_scene_dict(scene_dict, scene_filename):
        with open(scene_filename, "w") as o:
            json.dump(scene_dict, o)

    def push_scene_file(scene_filename):
        os.system(f"gsutil cp {scene_filename} {mkfiles_path}/scenebags/Sreyas")

    def set_duration(scene_dict, duration):
        scene_dict["durationMS"] = duration
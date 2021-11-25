#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import json 
import numpy as np
import os
import copy
from datetime import datetime

def all_equal(arr):
    flatten_arr = np.ravel(arr)
    return np.all(arr==flatten_arr[0])

def permutation(lst):
 
    # If lst is empty then there are no permutations
    if len(lst) == 0:
        return []
 
    # If there is only one element in lst then, only
    # one permutation is possible
    if len(lst) == 1:
        return [lst]
 
    # Find the permutations for lst if there are
    # more than 1 characters
 
    l = [] # empty list that will store current permutation
 
    # Iterate the input(lst) and calculate the permutation
    for i in range(len(lst)):
        m = lst[i]
 
       # Extract lst[i] or m from the list.  remLst is
       # remaining list
        remLst = lst[:i] + lst[i+1:]
 
       # Generating all permutations where m is first
       # element
        for p in permutation(remLst):
            l.append([m] + p)
    return l

def getLongestArray(x):
    n = 0;
    if (type(x) != dict):
        if (type(x) == list):
            n_new = len(x);
        else: 
            n_new = 0;

        return n_new;
    #if not an enumerable object
    else:
        for keys in x:
            if (keys != "baseVertexInd"):
                if (type(x[keys]) == list):
                    n_new = len(x[keys]);
                #IF array
                elif (type(x[keys]) == dict):
                    n_new = getLongestArray(x[keys]);
                #ELSE !array
                else:
                    n_new = 0;

                if (n_new > n):
                    n = n_new;
                #IF
            #IF array of raw vertexinds
        #FOR keys
    #IF object
    return n

def savetoFile(defaultContent, numset,filename):
    #save json files with the name including date and object, which variation changes, and number of trials
    allnumTrial = getLongestArray(defaultContent);

    allobj = list(defaultContent["OBJECTS"]);
    firstobj = allobj[0]
    paramStrategy = {"VIEW": "", "BACKGROUND": "", "SIZE": "", "POSITION": "", "LIGHTING": "", "CAMERA": ""}
    if (len(allobj) > 1):
        multiobj = "multi";
    saveDate = datetime.today().strftime("%Y%m%d");
    
    for obj in allobj:
        if (
            len(defaultContent["OBJECTS"][obj]["rotationDegrees"]["x"])>1 or
            len(defaultContent["OBJECTS"][obj]["rotationDegrees"]["y"]) > 1 or
            len(defaultContent["OBJECTS"][obj]["rotationDegrees"]["z"]) > 1
        ):
            paramStrategy["VIEW"] = "v";

        if (len(defaultContent["IMAGES"]["imageidx"]) > 1):
            paramStrategy["BACKGROUND"] = "b";

        if (len(defaultContent["OBJECTS"][obj]["sizeTHREEJS"]) > 1):
            paramStrategy["SIZE"] = "s";

        if (
            len(defaultContent["OBJECTS"][obj]["positionTHREEJS"]["x"]) > 1 or
            len(defaultContent["OBJECTS"][obj]["positionTHREEJS"]["y"]) > 1 or
            len(defaultContent["OBJECTS"][obj]["positionTHREEJS"]["z"]) > 1
        ):
            paramStrategy["POSITION"] = "p";

    for lt in list(defaultContent['LIGHTS']):
        if (
            len(defaultContent["LIGHTS"][lt]["position"]["x"]) > 1 or
            len(defaultContent["LIGHTS"][lt]["position"]["y"]) > 1 or
            len(defaultContent["LIGHTS"][lt]["position"]["z"]) > 1
        ):
            paramStrategy["LIGHTING"] = "l";
        
    if (len(defaultContent["CAMERAS"]["camera00"]["position"]["x"]) > 1 or
        len(defaultContent["CAMERAS"]["camera00"]["position"]["y"]) > 1 or
        len(defaultContent["CAMERAS"]["camera00"]["position"]["z"]) > 1 or
        len(defaultContent["CAMERAS"]["camera00"]["targetTHREEJS"]["x"]) > 1 or
        len(defaultContent["CAMERAS"]["camera00"]["targetTHREEJS"]["y"]) > 1 or
        len(defaultContent["CAMERAS"]["camera00"]["targetTHREEJS"]["z"]) >1
       ):
        paramStrategy["CAMERA"] = "c"
    
    if filename:
        newfileName = saveDate + "_" + filename + 'im' + str(allnumTrial) +"_dur" + \
        str(defaultContent["durationMS"][0]) + "ms" + ".json"

    else:
        newfileName = saveDate + "_" + "Var6" + paramStrategy["VIEW"] + paramStrategy["BACKGROUND"] + \
        paramStrategy["SIZE"] + paramStrategy["POSITION"] + paramStrategy["LIGHTING"] + paramStrategy["CAMERA"] + "_" + "set" + \
        str(numset) +"_" +"im" +str(allnumTrial) +"_" +firstobj +"-" +multiobj +"_dur" + \
        str(defaultContent["durationMS"][0]) + "ms" + ".json";
    print(newfileName)
    with open(newfileName, 'w') as json_file:
          json.dump(defaultContent, json_file,indent = 2)

def backbone(template_file,
camType,
camFOV,
camSetting,
                  
lightnamelist,
lightposlist,
                 
objnamelist,
objrotlist,
objsizelist,
objposlist,
objvisiblelist,
                  
durationMS,
bkgidx,
bkgsize,
             
meshpathfile
): 
    if type(template_file) == str:
        content = json.load(open(template_file))
    else:
        content = copy.deepcopy(template_file)
        
    #CAMERAS
    if len(camType) != 0:
        content["CAMERAS"]["camera00"]["type"] = camType;
    if type(camFOV) == int:
        content["CAMERAS"]["camera00"]["fieldOfView"] = camFOV;
    
    if len(camSetting) != 0: 
        content['CAMERAS']["camera00"]['position']['x'] = []
        content['CAMERAS']["camera00"]['position']['y'] = []
        content['CAMERAS']["camera00"]['position']['z'] = []
        content['CAMERAS']["camera00"]['targetTHREEJS']['x'] = []
        content['CAMERAS']["camera00"]['targetTHREEJS']['y'] = []
        content['CAMERAS']["camera00"]['targetTHREEJS']['z'] = []
        for c in camSetting:
            content['CAMERAS']["camera00"]['position']['x'].append(c[0])
            content['CAMERAS']["camera00"]['position']['y'].append(c[1])
            content['CAMERAS']["camera00"]['position']['z'].append(c[2])
            content['CAMERAS']["camera00"]['targetTHREEJS']['x'].append(c[3])
            content['CAMERAS']["camera00"]['targetTHREEJS']['y'].append(c[4])
            content['CAMERAS']["camera00"]['targetTHREEJS']['z'].append(c[5])
            

    #LIGHTS
    if len(lightnamelist) != 0:
        for i,lt in enumerate(lightnamelist):
            if len(lightposlist) != 0:
                
                if  len(lightposlist) == 1:
                    lightpos =  lightposlist[0]
                else:
                    lightpos = lightposlist[i]
                
                content['LIGHTS'][lt]['posititon']['x']  = [lightpos[0]]
                content['LIGHTS'][lt]['posititon']['y']  = [lightpos[1]]
                content['LIGHTS'][lt]['posititon']['z']  = [lightpos[2]]
            
    
    #OBJECTS
    if len(objnamelist) != 0:
        for i,obj in enumerate(objnamelist):
            content["OBJECTS"][obj] = {};
            
            if meshpathfile:
                m = json.load(open(meshpathfile))
                content["OBJECTS"][obj]["meshpath"] = m[obj];
            else:
                content["OBJECTS"][obj]["meshpath"] = "";
            content["OBJECTS"][obj]["objectdoc"] = "";
           
            content["OBJECTS"][obj]["material"] = {
                "type": "MeshPhysicalMaterial",
                "color": "#7F7F7F",
                "metalness": 0.25,
                "roughness": 0.65,
                "reflectivity": 0.5,
                "opacity": [1],
                "transparent": "false",
            };
            
            if len(objsizelist) != 0: 
                if len(objsizelist) == 1:
                    objsize = objsizelist[0]
                else:
                    objsize = objsizelist[i]

                content["OBJECTS"][obj]["sizeTHREEJS"] = [objsize];

            else:
                content["OBJECTS"][obj]["sizeTHREEJS"] = [];

            if len(objposlist) !=0:
                if len(objposlist) == 1:
                    objpos = objposlist[0]
                else:
                    objpos = objposlist[i]

                content["OBJECTS"][obj]["positionTHREEJS"] = { "x": [objpos[0]], 
                                                              "y": [objpos[1]], 
                                                              "z": [objpos[2]] };
            else:
                content["OBJECTS"][obj]["positionTHREEJS"] = { "x": [], 
                                                              "y": [], 
                                                              "z": [] };
            if len(objrotlist) !=0:
                if len(objrotlist) == 1:
                    objrot = objrotlist[0]
                else:
                    objrot = objrotlist[i]

                content["OBJECTS"][obj]["rotationDegrees"] = { "x": [objrot[0]], 
                                                              "y": [objrot[1]], 
                                                              "z": [objrot[2]] };
            else:
                content["OBJECTS"][obj]["rotationDegrees"] = { "x": [], 
                                                              "y": [], 
                                                              "z": [] };

            if len(objvisiblelist) != 0:
                if len(objvisiblelist) == 1:
                    objvisible = objvisiblelist[0]
                else: 
                    objvisible = objvisiblelist[i]
                    
                content["OBJECTS"][obj]["visible"] = [objvisible];
            else:
                content["OBJECTS"][obj]['visible']= []

#             content["OBJECTS"][obj]["morphTarget"] = []

    #IMAGES
    content["IMAGES"]["imagebag"] = "/mkturkfiles/scenebags/objectome3d/background/";
    
    if len(bkgidx) !=0:
        content["IMAGES"]["imageidx"] = bkgidx;
            
    if len(bkgsize) != 0:
        content["IMAGES"]["sizeTHREEJS"] = bkgsize;

    # TIME
    if len(durationMS) != 0:
        content["durationMS"] = durationMS;

    return content

def permute_obj_param(
scenefile,
objnamelist,
objparamType,
objparam
):
    # permute over multiple objects 
    # objnamelist should contain objects that are already in the scenefile provided
    # add new trials to the provided scenefile 
    scenefile_new = copy.deepcopy(scenefile)
    allobj = scenefile_new['OBJECTS'] 
      
    if len(objparam) != len(objnamelist):
        print("parameter array should either be 1 or equal to the length of the object name array")
    else:
        objparam = permutation(objparam);
        objparam = np.unique(objparam,axis = 0);
        objnamelist = np.tile(objnamelist,len(objparam))
        if objparam.ndim == 2:
            objparam = objparam.flatten()
        elif objparam.ndim > 2:
            objparam = objparam.reshape(-1,objparam.shape[-1])
            
        for i,obj in enumerate(objnamelist):
            if obj not in allobj:
                print('object is not part of scenefile') 
                break
            else:
                if objparamType == "visible":
                    scenefile_new["OBJECTS"][obj][objparamType].append(int(objparam[i]));
                elif (
                    objparamType == "positionTHREEJS" or
                    objparamType == "rotationDegrees"):   

                    scenefile_new["OBJECTS"][obj][objparamType]['x'].append(float(objparam[i][0]));
                    scenefile_new["OBJECTS"][obj][objparamType]['y'].append(float(objparam[i][1]));
                    scenefile_new["OBJECTS"][obj][objparamType]['z'].append(float(objparam[i][2]));
                elif objparamType == "sizeTHREEJS":
                    scenefile_new["OBJECTS"][obj][objparamType].append(float(objparam[i]));
                else:
                    print("wrong object param Type");
                    break
            
        return scenefile_new;
    
def prettyScenefile(scenefile):
    # make scenefile by pretty by removing duplicates in a parameter array 
     # make dictionary pretty
    #if all the elements of the array are the same, just keep 1 
    
    param_change = json.load(open('param_change.js'))
    content = copy.deepcopy(scenefile) 
    for param in param_change:
        if param == 'CAMERAS' or param == 'LIGHTS' or param == "OBJECTS":
            for obj in content[param]: # multiple objects 
                for sub_param in param_change[param]:
                    if 'position' in sub_param or 'rotation' in sub_param or 'target' in sub_param:
                        sub_sub_param = ['x','y','z']
                        for p in sub_sub_param: 
                            if all_equal(content[param][obj][sub_param][p]):
                                content[param][obj][sub_param][p] = [content[param][obj][sub_param][p][0]]
                    else:
                        if all_equal(content[param][obj][sub_param]):
                            content[param][obj][sub_param] = [content[param][obj][sub_param][0]]
        elif param == 'IMAGES' or param == 'IMAGEFILTERS' or param == 'OBJECTFILTERS': # IMAGES, FILTERS. 
            for sub_param in param_change[param]:
                if all_equal(content[param][sub_param]):
                    content[param][sub_param] = [content[param][sub_param][0]]
        elif param == 'durationMS':
            if all_equal(content[param]):
                content[param]= [content[param][0]]
                
    return content

def mergeScenefiles(filelist):
    # merge multiple scenefiles in the order of the files into one scenefile
    # files must have the same fields/structure
    # files must have the same 3d objects
    # parameters not in param_change are going to assume the parameters in the first scenefile from the filelist
    current_dir = os.getcwd()
    param_change = json.load(open(current_dir + '/param_change.js'))
    if type(filelist[0]) == str :
        firstContent = json.load(open(filelist[0]))
    else :
        firstContent = filelist[0]

    content_merged = copy.deepcopy(firstContent)

    allobj = list(firstContent['OBJECTS'].keys());
    alllight = list(firstContent['LIGHTS'].keys());
    defaultcam = firstContent['CAMERAS']['camera00']

    allTrial = []
    for file in filelist:

        if type(file) == str: 
            content = json.load(open(file))
        else :
            content = copy.deepcopy(file)

        contentobj =list(content['OBJECTS'].keys());
        contentlight = list(content['LIGHTS'].keys())
        contentcam = content['CAMERAS']['camera00']

        if not all(elem in allobj  for elem in contentobj):
            print('scenefiles don''t have the same objects')
            break

        if not all(elem in alllight for elem in contentlight):
            print('scenefiles don''t have the same lights')
            break

        if contentcam['type'] != defaultcam['type']:
            print('scenefiles don''t have the same camera type')
            break

        numTrial = getLongestArray(content);

        # Lengthen params by numTrial
        for param in param_change:
            if param == 'CAMERAS' or param == 'LIGHTS' or param == "OBJECTS":
                for obj in content[param]: # multiple objects 
                    for sub_param in param_change[param]:
                        if 'position' in sub_param or 'rotation' in sub_param or 'target' in sub_param:
                            sub_sub_param = ['x','y','z']
                            for p in sub_sub_param: 
                                if (len(content[param][obj][sub_param][p]) == 1):
                                    content[param][obj][sub_param][p] = np.repeat(content[param][obj][sub_param][p][0],numTrial).tolist()
                                elif len(content[param][obj][sub_param][p]) == 0:
                                     content[param][obj][sub_param][p] = np.repeat("",numTrial).tolist()
                        else:
                            if len(content[param][obj][sub_param]) == 1:
                                content[param][obj][sub_param] = np.repeat(content[param][obj][sub_param][0],numTrial).tolist()
                            elif len(content[param][obj][sub_param]) == 0:
                                content[param][obj][sub_param] = np.repeat("",numTrial).tolist()
            elif param == 'IMAGES' or param == 'IMAGEFILTERS' or param == 'OBJECTFILTERS': # IMAGES, FILTERS. 
                for sub_param in param_change[param]:
                    if len(content[param][sub_param]) == 1:
                        content[param][sub_param] = np.repeat(content[param][sub_param][0],numTrial).tolist()
                    elif len(content[param][sub_param]) == 0:
                        content[param][sub_param] = np.repeat("",numTrial).tolist()
            elif param == 'durationMS':
                if (len(content[param]) == 1) :
                    content[param] = np.repeat(content[param][0],numTrial).tolist();

       # create an array of all trials 
        fileTrial = []

        for n in range(numTrial):
            trial = []
            trial_param = []
            for param in param_change:
                if param == 'CAMERAS' or param == "LIGHTS" or param == "OBJECTS":
                    for obj in content[param]: # multiple objects 
                        for sub_param in param_change[param]:
                            if 'position' in sub_param or 'rotation' in sub_param or 'target' in sub_param:
                                sub_sub_param = ['x','y','z']
                                for p in sub_sub_param: 
                                    trial.append(content[param][obj][sub_param][p][n])
                                    trial_param.append(param + '-' + obj + '-' + sub_param +'-' +  p)
                            else:
                                trial.append(content[param][obj][sub_param][n])
                                trial_param.append(param + '-' + obj + '-' + sub_param)
                elif param == 'IMAGES' or param == 'IMAGEFILTERS' or param == 'OBJECTFILTERS': # IMAGES, FILTERS. 
                    for sub_param in param_change[param]:
                        trial.append(content[param][sub_param][n])
                        trial_param.append(param + '-' + sub_param)
                elif param == 'durationMS':
                    trial.append(content[param][n])
                    trial_param.append(param)
            fileTrial.append(trial)

        # Concatenate params 
        allTrial.extend(fileTrial)

    # remove duplicates in an array 
    allTrial_new = []
    seen = {}
    for x in allTrial:
        t_x = str(x)
        if t_x not in seen:
            allTrial_new.append(x)
            seen[t_x] = None

            
    # repopulate scenefile 
    
    # initiate with an empty array 
    for param in param_change:
        if param == 'CAMERAS' or param == 'LIGHTS' or param == "OBJECTS":
            for obj in content[param]: # multiple objects 
                for sub_param in param_change[param]:
                    if 'position' in sub_param or 'rotation' in sub_param or 'target' in sub_param:
                        sub_sub_param = ['x','y','z']
                        for p in sub_sub_param: 
                            content_merged[param][obj][sub_param][p] = [] 
                    else:
                        content_merged[param][obj][sub_param] = [] 
        elif param == 'IMAGES' or param == 'IMAGEFILTERS' or param == 'OBJECTFILTERS': # IMAGES, FILTERS. 
            for sub_param in param_change[param]:
                content_merged[param][sub_param] = [] 
        elif param == 'durationMS':
            content_merged[param] = [] 

    for n in range(len(allTrial_new)):
        for ind,t in enumerate(trial_param):
            dict_keys = t.split('-')
            if len(dict_keys) == 4:
                content_merged[dict_keys[0]][dict_keys[1]][dict_keys[2]][dict_keys[3]].append(allTrial_new[n][ind])
            elif len(dict_keys) == 3:
                content_merged[dict_keys[0]][dict_keys[1]][dict_keys[2]].append(allTrial_new[n][ind])
            elif len(dict_keys) == 2:
                content_merged[dict_keys[0]][dict_keys[1]].append(allTrial_new[n][ind])
            elif len(dict_keys) == 1:
                content_merged[dict_keys[0]].append(allTrial_new[n][ind])

    content_merged = prettyScenefile(content_merged)

    return content_merged;

def editScenefile(scenefile,paramObject,paramType,param):
    # replace scenefile params
           
    content = copy.deepcopy(scenefile)
    if 'camera' in paramObject:
        if paramType == 'camSetting':
            content['CAMERAS'][paramObject]['position']['x'] = []
            content['CAMERAS'][paramObject]['position']['y'] = []
            content['CAMERAS'][paramObject]['position']['z'] = []
            content['CAMERAS'][paramObject]['targetTHREEJS']['x'] = []
            content['CAMERAS'][paramObject]['targetTHREEJS']['y'] = []
            content['CAMERAS'][paramObject]['targetTHREEJS']['z'] = []
            for c in param:
                content['CAMERAS'][paramObject]['position']['x'].append(c[0])
                content['CAMERAS'][paramObject]['position']['y'].append(c[1])
                content['CAMERAS'][paramObject]['position']['z'].append(c[2])
                content['CAMERAS'][paramObject]['targetTHREEJS']['x'].append(c[3])
                content['CAMERAS'][paramObject]['targetTHREEJS']['y'].append(c[4])
                content['CAMERAS'][paramObject]['targetTHREEJS']['z'].append(c[5])
            
    elif 'light' in paramObject:
        if paramType == 'position':
            content['LIGHTS'][paramObject][paramType]['x'] = []
            content['LIGHTS'][paramObject][paramType]['y'] = []
            content['LIGHTS'][paramObject][paramType]['z'] = []
            for l in param: 
                content['LIGHTS'][paramObject][paramType]['x'].append(l[0])
                content['LIGHTS'][paramObject][paramType]['y'].append(l[1])
                content['LIGHTS'][paramObject][paramType]['z'].append(l[2])
        elif paramType == 'visible' or paramType == 'color' or paramType == 'intensity':  
            content['LIGHTS'][paramObject][paramType] = param
            
    elif 'duration' in paramObject:
        content['durationMS'] = param 
        
    elif 'IMAGES' in paramObject:
        if paramType == 'sizeTHREEJS' or paramType == 'imageidx':
            content['IMAGES'][paramType] = param
        
    elif 'IMAGEFILTERS' in paramObject:
        content['IMAGEFILTERS'][paramType] = param
        
    elif 'OBJECTFILTERS' in paramObject:
        content['OBJECTFILTERS'][paramType] = param
        
    else:
        if paramType == 'positionTHREEJS' or paramType ==  'rotationDegrees':
            content['OBJECTS'][paramObject][paramType]['x'] = []
            content['OBJECTS'][paramObject][paramType]['y'] = []
            content['OBJECTS'][paramObject][paramType]['z'] = []
            for o in param:
                content['OBJECTS'][paramObject][paramType]['x'].append(o[0])
                content['OBJECTS'][paramObject][paramType]['y'].append(o[1])
                content['OBJECTS'][paramObject][paramType]['z'].append(o[2])
        elif paramType == 'visible':
            content['OBJECTS'][paramObject][paramType] = param
            
    return content
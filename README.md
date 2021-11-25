# ScenefileGeneration
creates a json scenefile that runs on mkturk-lab

Current work flow is 
1) make a scenefile
2) upload it to the Google Cloud 
3) put its path in an agent param file
4) Run the agent on mkturk-lab 

Since there's no easy way to visualize your scene as you change these parameters in real-time, it's a good idea to have an intuition of how the numbers you put in a scenefile will actually translate to the screen. 

In a THREEJS environment, your objects (including camera) have 3D xyz coordinates. 

mkturk-lab renders 1 THREEJS unit as 1 inch on any screen, if that THREEJS object is placed at z = 10 away from a perspective camera. 

For example, if your scenefile contains a camera positioned at (0,0,10), and your object's sizeTHREEJS = 3 and is located at (0,0,0), the object will be rendered as 3 inches on the screen.
(More specifically, the largest dimension of the object will be 3 inches long.)

Now, if you move your camera away from the center, your object will look smaller on the screen by a factor of 10/(new camera distance from object). 

For example, take the same object as above. If the camera is at (0,0,100), your object will be rendered 3/(10/100) = 0.3 inches long. 


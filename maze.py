from sense_hat import SenseHat
import os.path
import sys
import numpy as np
import time

filename = "./maze_files/test2x2.txt"
green=(0,255,0)
orange=(255, 165, 0)
sense=SenseHat()
maxCol=8
maxRow=8
    
def draw_maze(maze,view_loc):
    
    for row in range(view_loc['row'],maxRow):
        for col in range(view_loc['col'],maxCol):
            if maze[row,col] == 1:
                sense.set_pixel(row,col, green)
                
def get_initial_marble_pos(maze):
    location={}
    location['x']=-1
    location['y']=-1
    
    size = np.shape(maze) 
    for row in range(0,size[0]):
        for col in range(0,size[1]):
            if maze[row,col] == 0:
                location['x']=col
                location['y']=row               
                return (location)
            
    return (location)
                
def update_marble_position(pitch,roll,x,y):    
    new_x=x
    new_y=y
    tolerance = 10
    
    #print('orig pitch is {0} orig roll is {1} pitch is {2} roll is {3} x is {4} y is {5}'.format(rest_pitch,rest_roll,pitch,roll,x,y))
    
    new_location={}    
    
    if 11 < pitch < 179:
        new_x-=1            
    elif 359 > pitch > 181:
        new_x+=1   
    
    if 11 < roll < 179:
        new_y+=1            
    elif 359 > roll > 181:
        new_y-=1   
    
    if 0 <= new_x < maxCol and 0 <= new_y < maxRow:
        maze_pixel = sense.get_pixel(new_x,new_y)        
        if maze_pixel[1] == 0:            
            x=new_x
            y=new_y
        
    sense.set_pixel(x,y, orange)       
    new_location['x']=x
    new_location['y']=y
    
    return new_location
    
def run(maze): 
    
    view_area={}
    view_area['row']=0
    view_area['col']=0
    
    marble_location = get_initial_marble_pos(maze)    
    if marble_location['x'] == -1 and marble_location['y'] == -1:
        print('No empty cells in maze')
        sys.exit()  
    
    while True:   
        o = sense.get_orientation()  
        sense.clear()
        draw_maze(maze,view_area)
        marble_location = update_marble_position(o["pitch"],o["roll"],marble_location['x'],marble_location['y'])
        
        time.sleep(0.1)

if not os.path.isfile(filename):
    print('% s does not exist.' % filename)
    sys.exit()
else:    
    maze = np.loadtxt(filename, dtype=int , skiprows = 1)
    run(maze)
  
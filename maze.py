from sense_hat import SenseHat
import os.path
import sys
import numpy as np
import time

filename = "./maze_files/test1x2.txt"
green=(0,255,0)
empty=(0,0,0)
orange=(255, 165, 0)
sense=SenseHat()
maxCol=8
maxRow=8
    
def draw_maze(maze,view_region,marble_location):    
    
    colStart = view_region['col_start']
    rowStart = view_region['row_start']
    newarr = (maze[rowStart:rowStart+maxRow:, colStart:colStart+maxCol]).flatten()
    
    asign = lambda t: green if t==1 else empty
    pixels = list(map(asign, newarr))
    
    sense.set_pixels(pixels)
    sense.set_pixel(marble_location['x']-colStart,marble_location['y']-rowStart, orange)
                
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
                
def update_marble_position(maze,pitch,roll,x,y,view_col,view_row):    
    new_x=x
    new_y=y   
    new_view_col=view_col
    new_view_row=view_row
    #print('orig pitch is {0} orig roll is {1} pitch is {2} roll is {3} x is {4} y is {5}'.format(rest_pitch,rest_roll,pitch,roll,x,y))
    print('x is {0} y is {1}'.format(x,y))
    new_locations={}
    marble_location = {}
    view_location = {}
    size = np.shape(maze) 
    
    if 11 < pitch < 179:
        new_x-=1            
    elif 359 > pitch > 181:
        new_x+=1   
    
    if 11 < roll < 179:
        new_y+=1            
    elif 359 > roll > 181:
        new_y-=1
        
    if 0 <= new_x < size[1] and 0 <= new_y < size[0]:
        if maze[new_y,new_x] == 0:
            if new_x>x and new_view_col+ maxCol < size[1]:
                new_view_col+=1
    
            if new_x<x and new_view_col > 0:
                new_view_col-=1
        
            if new_y>y and new_view_row+ maxRow < size[0]:
                new_view_row+=1
    
            if new_y<y and new_view_row > 0:
                new_view_row-=1
            x=new_x
            y=new_y
    
    marble_location['x']=x
    marble_location['y']=y
    view_location['row_start']=new_view_row
    view_location['col_start']=new_view_col
    
    new_locations['marble']=marble_location
    new_locations['view']=view_location
    
    #print('new view col {0} new view row {1}'.format(view_location['col_start'],view_location['row_start']))
    
    return new_locations
    
def run(maze):
    size = np.shape(maze)
    view_region = {}
    view_region['col_start']=0
    view_region['row_start']=0
    
    marble_location = get_initial_marble_pos(maze)    
    if marble_location['x'] == -1 and marble_location['y'] == -1:
        print('No empty cells in maze')
        sys.exit()  
    
    while True:   
        o = sense.get_orientation()  
        sense.clear()
        
        updated_locations = update_marble_position(maze,o["pitch"],o["roll"],marble_location['x'],marble_location['y'],view_region['col_start'],view_region['row_start'])
        marble_location = updated_locations['marble']
        view_region = updated_locations['view']
        draw_maze(maze,view_region,marble_location)
        time.sleep(0.1)

if not os.path.isfile(filename):
    print('% s does not exist.' % filename)
    sys.exit()
else:    
    maze = np.loadtxt(filename, dtype=int , skiprows = 1)
    
    print(maze)    
    
    run(maze)
  
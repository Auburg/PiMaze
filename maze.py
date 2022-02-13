from sense_hat import SenseHat
import os.path
import sys
import numpy as np
import time

filename = "./maze_files/test1x2.txt" #name of the maze file to load
green=(0,255,0) #colour for wall
empty=(0,0,0) #empty cell
orange=(255, 165, 0) #colour for marble
sense=SenseHat() #sense hat library
maxCol=8 # maximum number of screen pixel columns
maxRow=8 # maximum number of screen pixel rows

# this is the start of the program - check that the level file is valid. If not then print an error and exit 
if not os.path.isfile(filename):
    print('% s does not exist.' % filename)
    sys.exit()
else:    
    # the file exists - attempt to load the file into a 2d numpy array of ints, skipping the file header and then pass the array to the run function
    maze = np.loadtxt(filename, dtype=int , skiprows = 1)    
    run(maze)

# Function This is the main game loop which runs continuously
# Params: maze - the 2d maze level      
def run(maze):
  
    # initailise main game variables - view location starting from the top left corner
    view_region = {}
    view_region['col_start']=0
    view_region['row_start']=0
    
    # get initial marble position
    marble_location = get_initial_marble_pos(maze)    

    # if marble position cannot be determined then print an error and exit game
    if marble_location['x'] == -1 and marble_location['y'] == -1:
        print('No empty cells in maze')
        sys.exit()  
    
    # loop
    while True:   
        o = sense.get_orientation()  # get current sense hat orientation
        sense.clear() # clear the screen
        
        # update game position variables based on current sense hat pitch and roll values
        updated_locations = update_marble_position(maze,o["pitch"],o["roll"],marble_location['x'],marble_location['y'],view_region['col_start'],view_region['row_start'])
        marble_location = updated_locations['marble']
        view_region = updated_locations['view']

        # draw the current maze based on updated marble and view location
        draw_maze(maze,view_region,marble_location)

        # pause for a fraction of a second so we're not continuously polling the hardware
        time.sleep(0.1)
   
# Function which draws the current view of the maze 
# based on the view region within the maze level and the
# position of the marble 
# Params: maze - the 2d maze level view_region - the current x,y coordinates of the view location within the maze
# marble_location - the current x,y location of the marble
def draw_maze(maze,view_region,marble_location):    
    
    colStart = view_region['col_start'] # the the column and row values from the view region dictionary
    rowStart = view_region['row_start'] 

    # using these values, retrieve a 2d subset of the entire maze which we will draw and then flatten the 2d array 
    # to a 1d array for further processing
    viewArray = (maze[rowStart:rowStart+maxRow:, colStart:colStart+maxCol]).flatten()
    
    # the view array contains ints (0 or 1). We want to convert these to a rgb colour (green if 1, empty if 0)
    # we declare a lambda expression which can be used to map one to the other
    intToColurExp = lambda t: green if t==1 else empty

    #for each element in the view array apply the expression above and return a new list of pixel values
    pixels = list(map(intToColurExp, viewArray))
    
    #set all the maze pixels passing in the pixel array
    sense.set_pixels(pixels)

    #set the cell for the marble location, subtracting the view position to get the screen position
    sense.set_pixel(marble_location['x']-colStart,marble_location['y']-rowStart, orange)

# Function which determines the initial marble location for the maze by searching for the first empty cell
# Params: maze - the 2d maze level 
# Returns a dictionary containing the x,y marble location             
def get_initial_marble_pos(maze):
    location={}
    location['x']=-1 #declare default invalid locations - if no empty cell is found in the maze then this is what's
    location['y']=-1 # returned
    
    size = np.shape(maze) 
    for row in range(0,size[0]): # loop through the maze for the first empty cell and if ofund return the row, col value
        for col in range(0,size[1]):
            if maze[row,col] == 0:
                location['x']=col
                location['y']=row               
                return (location)
            
    return (location)

# Function which updates the state of the game based on the current sense hat pitch and roll values 
# Params: maze - the 2d maze level pitch - the current pitch value roll - the current roll value
# marble_x - the current marble column position marble_y - the current marble row position view_col - the current view start column
# view_row - the current view row position
# Returns a dictionary containing updated locations of the view location and marble position (each within their own dictionary)          
def update_marble_position(maze,pitch,roll,marble_x,marble_y,view_col,view_row):    
    new_x=marble_x #store the current game values for marble and view
    new_y=marble_y   
    new_view_col=view_col
    new_view_row=view_row
    
    #declare return values
    new_locations={}
    marble_location = {}
    view_location = {}
    size = np.shape(maze) 
    
    #use hard coded values to detect which direction the device is being moved - 
    if 11 < pitch < 179:
        new_x-=1  # if pitch is between these values then the player is pitching to the left so the new x position needs to move left          
    elif 359 > pitch > 181:
        new_x+=1   # if pitch is between these values then the player is pitching to the right so the new x position needs to move right  
    
    if 11 < roll < 179:
        new_y+=1  # if roll is between these values then the player is rolling downwards then the new y position needs to move down (increase in y)
    elif 359 > roll > 181:
        new_y-=1 # if roll is between these values then the player is rolling away then the new y position needs to move up (decrease in y)
        
    # we now have our updated x and y values - we need to check that they are within the limits of the maze level
    # i.e. col is between 0 and the maze max column and row is between 0 and max maze row 
    # we then need to check that the new marble position occupies an empty maze cell and not a wall
    # if that is the case then we need to compare the new marble position with the previous position in both x and y (i.e. the direction of travel) and update the
    # view position accordingly to show the view scrolling as the marble moves around. The view needs to move in the opposite direction of the marble.
    # However, the view position can only move if it's not going to move off the lower limits of the column and row (i.e. not less than 0) and not move off the maximum 
    # row and column of the maze (i.e. it cannot exceed max maze row/col-max row/col constant)
    # if these conditions are met then the marble and view values are updated otherwise they remain unchanged
    if 0 <= new_x < size[1] and 0 <= new_y < size[0]: 
        if maze[new_y,new_x] == 0:                   
            if new_x>marble_x and new_view_col+ maxCol < size[1]:
                new_view_col+=1
    
            if new_x<marble_x and new_view_col > 0:
                new_view_col-=1
        
            if new_y>marble_y and new_view_row+ maxRow < size[0]:
                new_view_row+=1
    
            if new_y<marble_y and new_view_row > 0:
                new_view_row-=1
            marble_x=new_x
            marble_y=new_y
    
    # return the updated view and marble positions in dictionaries
    marble_location['x']=marble_x
    marble_location['y']=marble_y
    view_location['row_start']=new_view_row
    view_location['col_start']=new_view_col
    
    new_locations['marble']=marble_location
    new_locations['view']=view_location
    
    return new_locations


import mdl
import os
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """
varied = False
frames = 0
basename = ""
    
def first_pass( commands ):
    global varied
    global frames
    global basename

    for command in commands:
        line = command[0]
        args = command[1:]

        if line == "vary":
            varied = True

        if line == "basename":
            basename = args[0]

        if line == "frames":
            frames = int(args[0])

    if varied and not(frames):
        exit()

    if frames and not(basename):
        basename = "jonalfdyrlandweaver"
        print "You forgot the basename, it is now jonalfdyrlandweaver."

    #return second_pass(commands, frames)

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""
knobs = []

def second_pass( commands, num_frames ):
    global knobs
    global frames
    
    if not(frames):
        exit()

    knobs = [{} for x in range(num_frames)]

    for command in commands:
        line = command[0]
        args = command[1:]

        if line == "vary":
            knobName = args[0]
            startFrame = args[1]
            endFrame = args[2]
            startValue = float(args[3])
            endValue = float(args[4])

            if ((endFrame - startFrame) <= 0):
                print "Hey bud your frames are negative..."
                return

            increment = (endValue - startValue) / (endFrame - startValue)
            currentFrame = 0.0

            #if our increment is negative, swap starterino and enderino framez
            if increment < 0:
                increment *= -1.0
                for frame in range(endFrame, startFrame - 1, -1):
                    knobs[frame][knobName] = currentFrame
                    currentFrame += increment
            else:
                for frame in range(startFrame, endFrame + 1, 1):
                    knobs[frame][knobName] = currentFrame
                    currentFrame += increment

def run(filename):
    """
    This function runs an mdl script
    """
    global frames
    global basename
    global knobs
    
    color = [255, 255, 255]
    tmp = new_matrix()
    ident( tmp )

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    first_pass(commands)
    second_pass(commands, frames)

    #if frames == 0
    if not(frames):
        frames = 1

    #run all this for all frames
    for frame in range(frames):
        tmp = new_matrix()
        ident(tmp)
        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        tmp = []
        step = 0.1
        
        for command in commands:
            print command
            c = command[0]
            args = command[1:]
            
            if c == 'box':
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'move':
                if args[3] != None:
                    a = knobs[frame][args[3]] * args[0]
                    b = knobs[frame][args[3]] * args[1]
                    c = knobs[frame][args[3]] * args[2]
                    args = (a, b, c, args[3])
                    
                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                if args[3] != None:
                    a = knobs[frame][args[3]] * args[0]
                    b = knobs[frame][args[3]] * args[1]
                    c = knobs[frame][args[3]] * args[2]
                    args = (a, b, c, args[3])
                    
                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                if args[2] != None:
                    a = knobs[frame][args[2]] * args[1]
                    args = (args[0], a, args[2])
                
                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                    matrix_mult( stack[-1], tmp )
                    stack[-1] = [ x[:] for x in tmp]
                    tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
            #name the animatino file
            name = 'anim/' + basename + ( 3 - len(str(frame)) ) * '0' + str(frame) + '.ppm'
            
            #make dir if no existerino
            if not os.path.exists('anim'):
                os.makedirs('anim')

            save_ppm(screen,name)
            clear_screen(screen)

        #and finally
        make_animation(basename)

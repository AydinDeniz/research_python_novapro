from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pywavefront
import numpy as np

# Global variables
camera_pos = [0, 0, 5]
camera_target = [0, 0, 0]
camera_up = [0, 1, 0]
light_pos = [5, 5, 5]

# Load 3D model
scene = pywavefront.Wavefront('path/to/model.obj')

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(
        camera_pos[0], camera_pos[1], camera_pos[2],
        camera_target[0], camera_target[1], camera_target[2],
        camera_up[0], camera_up[1], camera_up[2]
    )
    
    # Set up lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    
    # Render the 3D model
    for mesh in scene.meshes:
        glBegin(GL_TRIANGLES)
        for face in mesh.faces:
            for vertex in face:
                glVertex3f(*mesh.vertices[vertex])
        glEnd()
    
    glutSwapBuffers()

def reshape(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

def keyboard(key, x, y):
    global camera_pos, camera_target, camera_up
    if key == b'w':
        camera_pos = np.add(camera_pos, [0, 0, 0.1])
    elif key == b's':
        camera_pos = np.subtract(camera_pos, [0, 0, 0.1])
    elif key == b'a':
        camera_pos = np.subtract(camera_pos, [0.1, 0, 0])
    elif key == b'd':
        camera_pos = np.add(camera_pos, [0.1, 0, 0])
    elif key == b'q':
        camera_pos = np.subtract(camera_pos, [0, 0.1, 0])
    elif key == b'e':
        camera_pos = np.add(camera_pos, [0, 0.1, 0])
    glutPostRedisplay()

def mouse(button, state, x, y):
    global camera_target, camera_up
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        camera_target = np.add(camera_target, [0.1, 0, 0])
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_target = np.subtract(camera_target, [0.1, 0, 0])
    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"3D Rendering with PyOpenGL")
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse)
    glEnable(GL_DEPTH_TEST)
    glutMainLoop()

if __name__ == '__main__':
    main()
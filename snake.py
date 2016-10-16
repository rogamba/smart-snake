from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from random import randint
import os.path
import numpy as np
from numpy.linalg import inv

'''
Para python 3.0 en adelante
Cosas que faltan:
- Poner que si el usuario quiere moverse en dirección contraria al movimiento, no se haga nada
- Si la snake toca las paredes o a sí misma:
    1. Haga gameover -> se despliega mensaje y vuelve a empezar
    2. Se guarde la info en la db y se alimente la red neuronal
'''

# Variables del programa y a utilizar
window = 0                                             # glut window number
width, height = 500, 500                               # window size
field_width, field_height = 30, 30                     # internal resolution
interval = 140                                         # update interval in milliseconds

snake = [(10, 10)]                                     # snake list of (x, y) positions
snake_dir = (1, 0)                                     # snake movement direction
snake_dir_prev = (0,0)                                 # snake previous movement direction
food = []                                              # food list of type (x, y)
play = True
stop = False

# Variables globales
training_file = 'training_set.txt';
training_set=[]
n_in = 8;                                               # Dimensión de los vectores de entradas
n_out = 2;                                              # Dimensión de los vectores de salidas

# Listado de entrenamiento


# Cambia la variable de dirección al presionar una tecla
def keyboard(*args):
    symbols = "b'"
    key = args[0]
    for i in range(0,len(symbols)):
        key = str(key)
        key = key.replace(symbols[i],"")
    '''
    Poner condición de movimiento aquí
    '''
    # Importante! si le queremos cambiar el valor
    global snake_dir
    if key == 'w':
        snake_dir = (0, 1)                             # up
    if key == 's':
        snake_dir = (0, -1)                            # down
    if key == 'a':
        snake_dir = (-1, 0)                            # left
    if key == 'd':
        snake_dir = (1, 0)                             # right
    # Vemos si el usuario ya no quiere seguir jugando
    if key == 'e':
        global play
        play=False


def refresh2d_custom(width, height, internal_width, internal_height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, internal_width, 0.0, internal_height, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

def draw_rect(x, y, width, height):
    glBegin(GL_QUADS)                                  # start drawing a rectangle
    glVertex2f(x, y)                                   # bottom left point
    glVertex2f(x + width, y)                           # bottom right point
    glVertex2f(x + width, y + height)                  # top right point
    glVertex2f(x, y + height)                          # top left point
    glEnd()                                            # done drawing a rectangle

def draw_snake():
    glColor3f(1.0, 1.0, 1.0)                           # set color to white
    for x, y in snake:                                 # go through each (x, y) entry
        draw_rect(x, y, 1, 1)                          # draw it at (x, y) with width=1 and height=1

def draw_food():
    glColor3f(0.5, 0.5, 1.0)                           # set color to blue
    for x, y in food:                                  # go through each (x, y) entry
        draw_rect(x, y, 1, 1)                          # draw it at (x, y) with width=1 and height=1

def vec_add(m1, m2):
    x1,y1 = m1
    x2,y2 = m2
    return (x1 + x2, y1 + y2)

def update(value):
    snake.insert(0, vec_add(snake[0], snake_dir))      # insert new position in the beginning of the snake list
    snake.pop()                                        # remove the last element
    '''
    Estas funcinoes siempre se ejecutan
    no importa si se esta entrenando o no
     '''
    # Vemos si la serpiente llega a la comida
    (hx, hy) = snake[0]                                # get the snake's head x and y position
    for x, y in food:                                  # go through the food list
        if hx == x and hy == y:                        # is the head where the food is?
            snake.append((x, y))                       # make the snake longer
            food.remove((x, y))                        # remove the food
    # Si no hay comida, dibujar aleatoriamente
    if(len(food) == 0):
        x, y = randint(0, field_width-1), randint(0, field_height-1)
        food.append((x, y))
    '''
    Obtenemos los valores del vector P:
    dir_previa, dir_nueva, dir_min_manzana, dir_min_chocar
    '''
    global snake_dir
    global snake_dir_prev
    global action
    p_vector = buildVector(snake_dir,snake,food[0])
    p_test = np.mat(p_vector)
    snake_dir_prev = snake_dir

    # Si esta en entrenamiento el vector obtenido se aduntara al set de entrenamiento
    if(action == 'e'):
        vstring = '';
        # Parte de los inputs (arreglo de inputs)
        for i in range(0,n_in):
            vstring = vstring+str(p_vector[i,0])

        # Parte de los outputs
        vstring = vstring+","
        vdir = binDirection(snake_dir)
        for c in range(0,n_out):
            vstring = vstring+str(vdir[c])

        training_set.append(vstring)
    # Si esta corriendo, el vector que obtuvimos es el de pruebas, obtenemos la matriz de pesos para la siguiente direccion
    elif(action == 'c'):
        w_p = w_matrix*p_test
        new_dir = hardlims(w_p)                                      # Valuamos en la funcion hardlims para ver si es 1 o -1
        snake_dir = tuple(vectorDirection(new_dir))
        print(snake_dir)

    # Checamos si el usuario no ha presionado la teca de salir del juego

    if play:
        glutTimerFunc(interval, update, 0)             # Se llama a sí misma cada 200 milisegundos
    else:
        if action == 'e':
            fx = open(training_file,'w')
            for set in training_set:
                fx.write(set + "\n")
            fx.close()
        action = 'q'


def draw():                                            # draw is called all the time
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the screen
    glLoadIdentity()                                   # reset position
    refresh2d_custom(width, height, field_width, field_height)
    draw_food()                                        # draw the food
    draw_snake()                                       # Dibujamos la serpiente
    glutSwapBuffers()                                  # important for double buffering



def buildVector(dir,snake,food):
    vector = np.empty((n_in,1),np.int32)
    head_food = []

    # Ponemos las direcciones en terminos de -1 y 1
    vdir = binDirection(dir)

    # Direcciones a las que se encuentra la manzana (relativa a la cabeza y a la direccion)
    (head_x,head_y) = snake[0]
    head_food.append(food[0]-head_x)
    head_food.append(food[1]-head_y)
    dir_food = relativeDir(dir,head_food)

    # Distancia de la comida a la cabeza de la serpiente
    dist = int(( head_food[0]**2 + head_food[1]**2 )**0.5)
    bin_dist = "{:05b}".format(dist);

    # Direccion de la distancia mas larga a chocar ... pendiente

    # Construimos el vector P en string y matriz
    vector[0,0] = dir_food[0]                            # Direccion de la comida relativa la serpiente
    vector[1,0] = dir_food[1]
    vector[2,0] = dir_food[2]
    vector[3,0] = 1 if int(bin_dist[0]) > 0 else -1      # Distancia a la que se encuentra la comida
    vector[4,0] = 1 if int(bin_dist[1]) > 0 else -1
    vector[5,0] = 1 if int(bin_dist[2]) > 0 else -1
    vector[6,0] = 1 if int(bin_dist[3]) > 0 else -1
    vector[7,0] = 1 if int(bin_dist[4]) > 0 else -1

    return vector

def binDirection(dir):
    bin_dir = [-1,-1]
    if dir == (1,0):
        bin_dir = [-1,-1]
    elif dir == (0,1):
        bin_dir = [-1,1]
    elif dir == (-1,0):
        bin_dir = [1,-1]
    elif dir == (0,-1):
        bin_dir = [1,1]
    return bin_dir

def vectorDirection(dir):
    vec_dir = [1,0]
    if dir == (0,0):
        vec_dir = [1,0]
    elif dir == (0,1):
        vec_dir = [0,1]
    elif dir == (1,0):
        vec_dir = [-1,0]
    elif dir == (1,1):
        vec_dir = [-1,0]
    return vec_dir

'''
Dependiendo de la direccion de la serpiente, obtenemos la posicion relativa de la manzana
    010 - enfrente
    100 - izquierda
    001 - derecha
'''
def relativeDir(dir,vector):
    rel_vector = [0,0]
    dir_food = [-1,-1,-1]

    # Si va para arriba
    if dir == (0,1):
        rel_vector[0] = vector[0]
        rel_vector[1] = vector[1]
    # Si va a la derecha
    elif dir == (1,0):
        rel_vector[0] = -vector[1]
        rel_vector[1] = vector[0]
    # Si va a la izquierda
    elif dir == (-1,0):
        rel_vector[0] = vector[1]
        rel_vector[1] = -vector[0]
    # Si va para abajo
    elif dir == (0,-1):
        rel_vector[0] = -vector[0]
        rel_vector[1] = -vector[1]

    # generamos la entrada de las direcciones de la manzana
    if rel_vector[1] > 0:
        dir_food[1] = 1
    if rel_vector[0] > 0:
        dir_food[2] = 1
    elif rel_vector[0] < 0:
        dir_food[0] = 1

    return dir_food

def hardlims(vector):
    new_vector = [0,0]
    new_vector[0] = 1 if vector[0,0] >= 0 else 0
    new_vector[1] = 1 if vector[1,0] >= 0 else 0
    return tuple(new_vector)


'''
Empieza la interfaz con el usuario
- Pregunta si quiere entrenar o correr el set de entrenamieto
'''
print("------------------------------")
print("           Smart Snake        ")
print("------------------------------")
    # Preguntar qué acción desea realizas
while True:
    try:
        action_str = input('Selecciona una opción (Entrenar[e] / Correr[c]): ')
        if (action_str.lower() == 'e' or action_str.lower() == 'c' or action_str.lower() == 'entrenar' or action_str.lower() == 'correr'):
            action = action_str[0].lower();
            break
        else:
            print("Debes seleccionar una opción")
    except:
        break

# Si selecciona que entrenar
    # Guardamos en variable para que en cada loop se guarde:
        # - dirección de movimiento previa
        # - dirección de movimeinto nueva
        # - dirección de la distancia más cora a la manzana
        # - dirección distancia mas larga de la pared o la cola
if (action == 'c'):
    #Revisamos si existe el archivo -> Si existe generar matrices de entrenamiento conlos datos
    if (os.path.isfile(training_file)):
        data_read = open(training_file , 'r')
        data_text = data_read.read()
        data_read.close()
        tr_set = data_text.rstrip().split('\n')
        # Iteramos por el set para generar matriz de entradas y de salidas
        c=0
        inputs = np.empty((n_in,len(tr_set)),np.int32)
        outputs = np.empty((n_out,len(tr_set)),np.int32)
        for set in tr_set:
            set_arr = set.split(',')
            # Creamos matriz de entradas
            d=0
            val_str=''
            for i in range(0,len(set_arr[0])):
                val_str+=set_arr[0][i]
                if val_str != '-':
                    inputs[d,c] = int(val_str)
                    val_str=''
                    d=d+1
            # Creamos matriz de salidas
            d=0
            val_str=''
            for j in range(0,len(set_arr[1])):
                val_str+=set_arr[1][j]
                if val_str != '-':
                    outputs[d,c] = int(val_str)
                    val_str=''
                    d=d+1
            c+=1
        # Obtenemos los pesos
        p_matrix = np.mat(inputs)
        t_matrix = np.mat(outputs)
        w_matrix = t_matrix*p_matrix.getI()
    # Si no -> el usuario debe jugar para generar el set de entrenamiento
    else:
        print('No existe un set de entrenamiento, deberás jugar para entrenar a la serpiente!')
        action = 'e'

# Si selecciona que correr, vemos si existe el archivo del set de entrenamiento
    # Si no existe, poner a jugar al usuario ...
    # Si existe el archivo...
        # Leemos el archivo y guardamos en una variable (arreglo de numpy)
        # Obtenemos variables solicitadas al guardar el set del movimiento actual
        # Resolvemos la red con el set de entrenamiento para predecir el siguiente movimiento
        # ...
if (action == 'e'):
    print("Presiona 'e' para detener el entrenamiento.")



# Glut
glutInit()                                             # initialize glut
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
glutInitWindowSize(width, height)                      # set window size
glutInitWindowPosition(0, 0)                           # set window position
window = glutCreateWindow(b"ANN Snake")                 # create window with title
glutDisplayFunc(draw)                                  # set draw function callback
glutIdleFunc(draw)                                     # draw all the time
glutTimerFunc(interval, update, 0)                     # trigger next update
# Si esta en entrenamiento, leemos el teclado
glutKeyboardFunc(keyboard)                             # Dice a opengl que queremos revisar si hay presión de teclado
glutMainLoop()



'''
Guardar contenido en un archivo:
csv = response.read()
csv_str = str(csv)
lines = csv_str.split('\\n')
dest_url = r'goog.csv' # r dice que es raw string
fx = open(dest_url,'w')
for line in lines:
    fx.write(line + "\n")
fx.close();
'''

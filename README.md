#Smart Snake
Supervised Hebbian learning for the snake game

## What is this?
Snake game built with python and opengl that uses a training set recorded from a player to build a Hebbian non auto associative neural network to predict the output of each movement based
on the position of the head of the snake relative to the position of the apple

## Input Matrix
To generate the input vectors of the matrix, we consider the following variables:  
* Position of the food relative to the position of the food and it's direction (3 bits
* Distance of the food relative to the head of the snake (5 bits)

The input vectors have 8 values, it means that they are in the R^8 vector space. the first 3 values indicate the position of the food relative to the head, and they can have
different values depending on the location of the food, for example:
* 010 - The apple is right in front of the snake
* 001 - The apple is right from the head
* 100 - THe apple is left from the head
And alse there can be combinations of these values, for example 110 would indicate the apple is left and front of the direction of the head in that moment.

The last 5 bits of the input vectors indicate the distance between the apple and the head, assuming that in the training set the decreasing of this 5 bits value
will indicate that the head is moving towards the right direction.

## Output vector
To every input vector p, corresponds an output vector t (2x1) of 2 bits that indicates the direction of the next move of the snake, the values can be:
* -1, -1: right
* -1, 1: up
* 1, -1: left
* 1, 1: down
Having the combination of inputs and outputs we can generate the training set and P and T matrices

## Training the net
Run the script with python snake.py and choose the option "Train", then play for a while. At the end of the training all your movements will be saved
in a file, which will be the training set matrix for the hebbian net. The output of every movement relative to the position of the apple will then be calculated.

## How it works?
1. To start the snake execute
```
python snake.py
```
2. Select train snake to generate your training set file
3. Run the snake again with the previous command, this time select run
4. Watch how good your training was

## Improvements
* Add backpropagation algorithm to improve learning
* Make more user-friendly the gui

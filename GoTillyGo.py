import turtle
import sys
import random

tile_size = 30
fountain_size = 360
fountain = [] * 144
gameboard = [0] * 144

def main(argv):
    #read in file with genome using file name as only argument
    f = open(argv[0],"r")
    if f.mode == "r":
        strDict = f.read()
    f.close()
    genome = eval(strDict)

    #initialize the game
    loadWindow = turtle.Screen()
    create_gameboard()
    draw_fountain()
    play_game(genome)
    loadWindow.mainloop()

#called once at the beginning of the game to draw the fountain
#drawn using the text-based gaemboard
#the bottom left corner of the grid is 0,0. The tiles ascend by
def draw_fountain():
    x = -fountain_size/2
    y = -fountain_size/2
    for i in range(0,12):
        for j in range(0,12):
            t = tile("white",x,y)
            if gameboard[(i*12) + j] == 3:
                t.color = "gray"
            if gameboard[(i*12) + j] == 2:
                t.color = "red"
            if gameboard[(i*12) + j] == 1:
                t.color = "white"
            t.draw_square()
            x += tile_size
            fountain.append(t)
        x = -fountain_size/2
        y += tile_size

def create_gameboard():
    for i in range(0,144):
        if i < 12:
            gameboard[i] = 3
        elif i > 132:
            gameboard[i] = 3
        elif i%12 == 0:
            gameboard[i] = 3
        elif i%12 == 11:
            gameboard[i] = 3
        else:
            gameboard[i] = random.randrange(1, 3)


def play_game(genome):
    origin_tiles = [13, 22, 121, 130]
    current_tile = random.choice(origin_tiles)
    fountain[current_tile].update_Tilly(0)
    for i in range(0,200):
        key = get_tilly_von_neumann(current_tile)
        #print(key)
        action = genome.get(key)
        #print(action)
        previous_tile = current_tile
        if action == 0:  # do nothing
            fountain[current_tile].update_Tilly(i)
            pass
        if action == 1:
            fountain[current_tile].update_square()
            current_tile += 12  # move up
            fountain[current_tile].update_Tilly(i)
        if action == 2:
            fountain[current_tile].update_square()
            current_tile += 1  # move right
            fountain[current_tile].update_Tilly(i)
        if action == 3:
            fountain[current_tile].update_square()
            current_tile -= 12  # move down
            fountain[current_tile].update_Tilly(i)
        if action == 4:
            fountain[current_tile].update_square()
            current_tile -= 1  # move left
            fountain[current_tile].update_Tilly(i)
        if action == 5:
            fountain[current_tile].update_square()
            current_tile += random.choice([1, 12, -1, -12])  # move in a random direction
            fountain[current_tile].update_Tilly(i)
        if action == 6:
            if gameboard[current_tile] == 1:  # good tile replacement
                pass
            elif gameboard[current_tile] == 2:  # bad tile replacement
                gameboard[current_tile] = 1
                fountain[current_tile].color = "white"  # replace the tile
                fountain[current_tile].update_square()
                fountain[current_tile].update_Tilly(i)
        if gameboard[current_tile] == 3:  # check if on boundry tile
            fountain[current_tile].update_square()
            current_tile = previous_tile
            fountain[current_tile].update_Tilly(i)
            pass  # move tilly back to board space

def get_tilly_von_neumann(tilly_position):
    von_nuemann = ""
    von_nuemann += str(gameboard[tilly_position])  # current tile you are on
    von_nuemann += str((gameboard[(tilly_position + 12) % 144]))  # above
    von_nuemann += str((gameboard[(tilly_position - 12) % 144]))  # below
    von_nuemann += str(gameboard[tilly_position - 1])  # left
    von_nuemann += str(gameboard[tilly_position + 1])  # right
    return int(von_nuemann)

class tile(object):
    def __init__(self, color, x, y):
        self.xcor = x
        self.ycor = y
        self.color = color

    def draw_square(self):
        patches = turtle.Turtle()
        patches.hideturtle()
        patches._tracer(0,0)
        patches.color("black", self.color)
        patches.up()
        patches.goto(self.xcor, self.ycor)
        patches.down()
        patches.begin_fill()
        for i in range(0,4):
            patches.forward(tile_size)
            patches.left(90)
        patches.end_fill()
        turtle.update()

    def update_square(self):
        patches = turtle.Turtle()
        patches.hideturtle()
        patches._tracer(0, 0)
        patches.color("black", self.color)
        patches.up()
        patches.goto(self.xcor, self.ycor)
        patches.down()
        patches.begin_fill()
        for i in range(0, 4):
            patches.forward(tile_size)
            patches.left(90)
        patches.end_fill()
        turtle.update()


    '''def update_square(self):
        stef = turtle.Turtle()
        stef.penup()
        stef.hideturtle()
        stef.goto(self.xcor, self.ycor)
        stef.color("black", self.color)
        #stef.pendown()
        stef.begin_fill()
        for i in range(0, 4):
            stef.forward(tile_size)
            stef.left(90)
        stef.end_fill()
        turtle.update()'''

    def update_Tilly(self, i):
        stef = turtle.Turtle()
        stef.hideturtle()
        stef.color("black")
        stef.penup()
        stef.goto(self.xcor + 5, self.ycor + 5)
        stef.write(i+1)






if __name__ == "__main__":
    main(sys.argv[1:])







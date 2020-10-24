# 행렬의 성분값을 바꾸어 다른 색으로 표현하기

import turtle                                # 그래픽 처리를 위한 모듈
import numpy as np                           # 벡터, 행렬 데이터를 쉽게 처리하기 위한 모듈

myImg = np.array([[0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 1, 1, 1, 0, 0, 0, 0],
                  [1, 1, 1, 1, 1, 0, 0, 0],
                  [1, 1, 1, 1, 1, 0, 0, 0],
                  [0, 1, 1, 1, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0]])

pixelSize = 10

def putPixel(x, y, pSize, pCol):
    turtle.penup()
    turtle.goto(x*pSize,(-1)*y*pSize)
    turtle.pendown()
    turtle.begin_fill()
    turtle.fillcolor(pCol)
    turtle.setheading(45)
    turtle.circle(pSize/2, steps = 4)
    turtle.end_fill()

for j in range (0, 8) :
    for i in range (0, 8) :
        if (myImg[j][i] > 0):
            putPixel(i,j,pixelSize, "blue")
        else:
            putPixel(i,j,pixelSize, "white")

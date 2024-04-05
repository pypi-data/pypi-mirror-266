# A spanish translation of ColabTurtle from Tolga Atam: https://github.com/tolgaatam/ColabTurtle

Turtle for Google Colab notebooks
===================

Installation for Google Colab:
----
Create an empty code cell and type:

    !pip3 install SeTeEscapoLaTortuga

Run the code cell. Google Colab will install the library.


Usage
----
In any code cell, import like following:

    from SeTeEscapoLaTortuga.Turtle import *

As Colab stores the declared variables in the runtime, call this before using: 

    despertar_tortuga()


API
----
This module's API is mostly identical to the traditional turtle API. There are some differences, most notably: the angles are handled differently. 0 angle is east and the angles increase clockwise. Some functions from the traditional turtle library is missing here; however almost all the main functionality is implemented. The functions that this library implements are explained below:


`adelante(units)` -> Moves the turtle in the direction it is facing, by `units` pixels

`atras(units)` -> Moves the turtle in the opposite of the direction it is facing, by `units` pixels

<br/>

`derecha(degrees)` -> Turns the turtle to right by the given `degrees` many degrees.

`direccion(degrees)` -> Turns the turtle to the direction given as `degrees`

`izquierda(degrees)` -> Turns the turtle to left by the given `degrees` many degrees.

<br/>

`dibujar()` -> Lifts the pen, turtles movement will not draw anything after this function is called.

`no_dibujar()` -> Puts the pen down, causing the turtle movements to start drawing again.

<br/>

`velocidad(s)` -> Sets the speed of turtle's movements. `s` can be a value in interval [1,13] where 1 is the slowest and 13 is the fastest. If `s` is omitted, the function returns the current speed.

<br/>

`mover_a_x(x)` -> Moves the turtle to the given `x` position, the y coordinate of the turtle stays the same.

`mover_a_y(y)` -> Moves the turtle to the given `y` position, the x coordinate of the turtle stays the same.

`ir_a_casa()` -> Takes the turtle to the beginning position and angle. The turtle will continue drawing during this operation if the pen is down.

<br/>

`xcor()` -> Returns the current x coordinate of the turtle.

`ycor()` -> Returns the current y coordinate of the turtle.

`posicion()` -> Returns the current x,y coordinates of the turtle as a tuple.

`obtener_direccion()` -> Returns the direction that the turtle is looking at right now, in degrees.

<br/>

<br/>

`ir_a_xy(x,y)` Moves the turtle to the point defined by x,y. The coordinates can be given separately, or in a single tuple.

<br/>

<br/>

`mostrar_tortuga()` -> Makes the turtle visible.

`ocultar_tortuga()` -> Makes the turtle invisible.

`es_visible()` -> Returns whether turtle is currently visible as boolean.

<br/>

<br/>

```
color_de_fondo()
color_de_fondo(r,g,b)
bgccolor_de_fondoolor((r,g,b))
color_de_fondo(colorstring)
```
If no parameter given, returns the current background color as string. Else, changes the background color of the drawing area. The color can be given as three separate color arguments as in the RGB color encoding: red,green,blue. These three numbers can be given in a single tuple as well. The color can be given as a single color string, too! The following formats are accepted for this color string:
- HTML standard color names: 140 color names defined as standard ( https://www.w3schools.com/colors/colors_names.asp ) . Examples: `"red"`, `"black"`, `"magenta"`, `"cyan"` etc.
- Hex string with 3 or 6 digits, like `"#fff"`, `"FFF"`, `"#dfdfdf"`, `"#DFDFDF"`
- RGB string, like `"rgb(10 20 30)"`, `"rgb(10, 20, 30)"`

<br/>

<br/>

```
color() | pencolor()
color(r,g,b) | pencolor(r,g,b)
color((r,g,b)) | pencolor((r,g,b))
color(colorstring) | pencolor(colorstring)
```
The same as `bgcolor` but works with the turtle's pen's color.

<br/>

<br/>

`ancho_linea(w)` -> Changes the width of the pen. If the parameter is omitted, returns the current pen width.

<br/>

<br/>

```
distancia(x,y)
distancia((x,y))
```
Returns the turtle's distance to a given point x,y. The coordinates can be given separately or as a single tuple.

<br/>

<br/>

`borrar_todo()` -> Clear any drawing on the screen.

`escribir(obj, align=, font=)` -> Writes the string equivalent of any value to the screen. `align` and `font` **named** parameters can be given as arguments optionally. `align` must be one of `"left","center","right"`. It specifies where to put the text with respect to the turtle. `font` must be a tuple of three values like `(20, "Arial", "bold")`. The first value is the size, second value is the font family (only the ones that your browser natively supports must be used), the third value is font style that must be one of `"normal","bold","italic","underline"`.

`forma_de_la_tortuga(sh)` -> Takes a shape name `sh` and transforms the main character's look. This library only has `'circle'` and `'turtle'` shapes available. If no argument is supplied, this function returns the name of the current shape.

`ancho_de_la_ventana()` -> Return the width of the turtle window.

`alto_de_la_ventana()` -> Return the height of the turtle window.

<br/>

<br/>

<br/>

HAVE FUN DRAWING!

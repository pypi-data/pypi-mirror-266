Light image reader   |   Lector ligero de imagenes
==========================

[*ENGLISH*]
It is a light image reader with functions for use with tkinter.
This reader created it with the intention that it would be easier to use with the tkinter module (*and customtkinter*)

[*ESPAÑOL*]
Es un lector de imagenes ligero con funciones para usar con tkinter.
Este lector lo cree con la intencion de que fuera mas sencillo usar con el modulo tkinter (*y customtkinter*)


Installation (*pip or setup*)
=============================

+ With pip : 

  1. ``pip install LeerImagenes``


Usage
=================




.. code::

    # IMPORT MODULE        |   IMPORTAR MODULO
	import LeerImagenes as li
	
	# CREATE CANVAS IMAGE  |   CREAR UN LIENZO EN BLANCO
	image = createImage(32, 32)
	
	# FILL RECTANGLE RED   |   PINTAR UN RECTANGULO ROJO
	drawRectangle(image, 0,0, 32, 32, (255,0,0,255))
	
	# SAVE FIRST FILE      |   GUARDAR PRIMER ARCHIVO
	saveImageToFile(image, IMGMODE_PNG, "outputx32.png")
	
	# CHANGE THE SIZE      |   CAMBIAR EL TAMAÑO
	scaleImage(image, 320, 320)
	
	# DRAW TWO LINES       |   DIBUJAR DOS LINEAS
	drawLine(image, 0,0, 319,319, (0,255,255,255), 8)
	drawLine(image, 319,0, 0,319, (0,255,255,255), 8)
	
	# SAVE SECOND FILE     |   GUARDAR SEGUNDO ARCHIVO
	saveImageToFile(image, IMGMODE_PNG, "outputx320.png")
	
	# CHANGE THE SIZE      |   CAMBIAR EL TAMAÑO
	scaleImage(image, 64, 64)
	
	# SAVE THIRD FILE      |   GUARDAR TERCER ARCHIVO
	saveImageToFile(image, IMGMODE_PNG, "outputx64.png")





# -*- coding: utf-8 -*-
#   Copyright (C) 2023-2024 Samuele Carcagno <sam.carcagno@gmail.com>
#   This file is part of audiometry_trainer

#    audiometry_trainer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    audiometry_trainer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with audiometry_trainer.  If not, see <http://www.gnu.org/licenses/>.

from matplotlib.path import Path
import numpy as np

## ##################################
## BONE LEFT UNMASKED

verts = [
    (0, 0),
    (5, 5),
    (0, 10),

    (5, 5),
    (0, 0),
]

codes = [
    Path.MOVETO, #begin drawing
    Path.LINETO, 
    Path.LINETO, 

    Path.LINETO, 
    Path.LINETO, 
]

pth = Path(verts, codes)
pth.vertices[:,1] = pth.vertices[:,1]-5
pth.vertices[:,0] = pth.vertices[:,0]-2.5
pth.vertices = pth.vertices/10
bone_L_unm = pth

## ##################################
## BONE LEFT UNMASKED NO RESPONSE

verts = [
    (0, 0),
    (5, 5),
    (0, 10),

    (5, 5),
    (0, 0),

    (0, 0),
    (1, -1),
    (1, -1),
    (2, 0),
    (2, -2),
    (0, -2),
    (1, -1),
]

codes = [
    Path.MOVETO, #begin drawing
    Path.LINETO, 
    Path.LINETO, 

    Path.LINETO, 
    Path.LINETO,

    Path.MOVETO, 
    Path.LINETO,
    Path.MOVETO, 
    Path.LINETO,
    Path.LINETO,
    Path.LINETO,
    Path.LINETO, #close shape. This is not required for this shape but is "good form"
]

pth = Path(verts, codes)
pth.vertices[:,1] = pth.vertices[:,1]-5
pth.vertices[:,0] = pth.vertices[:,0]-2.5
pth.vertices = pth.vertices/10
bone_L_unm_NR = pth

## ##################################
## BONE RIGHT UNMASKED

verts = [
    (0, 0),
    (-5, 5),
    (0, 10),

    (-5, 5),
    (0, 0),
]

codes = [
    Path.MOVETO, 
    Path.LINETO, 
    Path.LINETO, 

    Path.LINETO, 
    Path.LINETO, 
]

pth = Path(verts, codes)
pth.vertices[:,1] = pth.vertices[:,1]-5
pth.vertices[:,0] = pth.vertices[:,0]+2.5
pth.vertices = pth.vertices/10
bone_R_unm = pth

## ##################################
## BONE RIGHT UNMASKED NR

verts = [
    (0, 0),
    (-5, 5),
    (0, 10),

    (-5, 5),
    (0, 0),

    (0, 0),
    (-1, -1),
    (-1, -1),
    (-2, 0),
    (-2, -2),
    (0, -2),
    (-1, -1),
]

codes = [
    Path.MOVETO, #begin drawing
    Path.LINETO, 
    Path.LINETO, 

    Path.LINETO, 
    Path.LINETO,

    Path.MOVETO, 
    Path.LINETO,
    Path.MOVETO, 
    Path.LINETO,
    Path.LINETO,
    Path.LINETO,
    Path.LINETO, #close shape. This is not required for this shape but is "good form"
]

pth = Path(verts, codes)
pth.vertices[:,1] = pth.vertices[:,1]-5
pth.vertices[:,0] = pth.vertices[:,0]+2.5#-3
pth.vertices = pth.vertices/10
bone_R_unm_NR = pth


## ##################################
## BONE LEFT MASKED 

verts = [
    (-4, 10),
    (0, 10),
    (0, 0),
    (-4, 0),

    (0, 0),
    (0, 10),
    (-4, 10),
]

codes = [
    Path.MOVETO, #begin drawing
    Path.LINETO, 
    Path.LINETO, 
    Path.LINETO,

    Path.LINETO, 
    Path.LINETO, 
    Path.LINETO,
]

pth = Path(verts, codes)
pth.vertices[:,1] = pth.vertices[:,1]-5
pth.vertices[:,0] = pth.vertices[:,0]+2
pth.vertices = pth.vertices/10
bone_L_msk = pth

## ##################################
## BONE RIGHT MASKED
verts = [
    (4, 10),
    (0, 10),
    (0, 0),
    (4, 0),

    (0, 0),
    (0, 10),
    (4, 10),
]

codes = [
    Path.MOVETO, #begin drawing
    Path.LINETO, 
    Path.LINETO, 
    Path.LINETO,

    Path.LINETO, 
    Path.LINETO, 
    Path.LINETO,
]

pth = Path(verts, codes)
pth.vertices[:,1] = pth.vertices[:,1]-5
pth.vertices[:,0] = pth.vertices[:,0]-2
pth.vertices = pth.vertices/10
bone_R_msk = pth


## ##################################
## BONE LEFT MASKED NO RESPONSE
verts = [
    (-4, 10),
    (0, 10),
    (0, 0),
    (-4, 0),

    (0, 0),
    (0, 10),
    (-4, 10),
    
    (0, 0),
    (1, -1),
    (1, -1),
    (2, 0),
    (2, -2),
    (0, -2),
    (1, -1),
]

codes = [
    Path.MOVETO, #begin drawing
    Path.LINETO, 
    Path.LINETO, 
    Path.LINETO,

    Path.LINETO, 
    Path.LINETO, 
    Path.LINETO,

    Path.MOVETO, 
    Path.LINETO,
    Path.MOVETO, 
    Path.LINETO,
    Path.LINETO,
    Path.LINETO,
    Path.LINETO, #close shape. This is not required for this shape but is "good form"
]

pth = Path(verts, codes)
pth.vertices[:,1] = pth.vertices[:,1]-5
pth.vertices[:,0] = pth.vertices[:,0]+2
pth.vertices = pth.vertices/10
bone_L_msk_NR = pth

## ##################################
## BONE RIGHT MASKED NO RESPONSE
verts = [
    (4, 10),
    (0, 10),
    (0, 0),
    (4, 0),

    (0, 0),
    (0, 10),
    (4, 10),
    
    (0, 0),
    (-1, -1),
    (-1, -1),
    (-2, 0),
    (-2, -2),
    (0, -2),
    (-1, -1),
]

codes = [
    Path.MOVETO, #begin drawing
    Path.LINETO, 
    Path.LINETO, 
    Path.LINETO,

    Path.LINETO, 
    Path.LINETO, 
    Path.LINETO,

    Path.MOVETO, 
    Path.LINETO,
    Path.MOVETO, 
    Path.LINETO,
    Path.LINETO,
    Path.LINETO,
    Path.LINETO, #close shape. This is not required for this shape but is "good form"
]

pth = Path(verts, codes)
pth.vertices[:,1] = pth.vertices[:,1]-5
pth.vertices[:,0] = pth.vertices[:,0]-2
pth.vertices = pth.vertices/10
bone_R_msk_NR = pth


## ##################################
## AIR RIGHT MASKED
verts = [
    (0, 10),
    (5, 0),
    (-5, 0),
    (0, 10),
    (-5, 0),
    (5, 0),
    (0, 10)

]

codes = [
    Path.MOVETO, #begin drawing
    Path.LINETO, 
    Path.LINETO, 
    Path.LINETO,
    Path.LINETO, 
    Path.LINETO, 
    Path.LINETO,

]

pth = Path(verts, codes)
pth.vertices[:,1] = pth.vertices[:,1]-5
pth.vertices[:,0] = pth.vertices[:,0]#-5
pth.vertices = pth.vertices/10
air_R_msk = pth

## ##################################
## AIR RIGHT MASKED NO RESPONSE
verts = [
    (0, 10),
    (5, 0),
    (-5, 0),
    (0, 10),
    (-5, 0),
    (5, 0),
    (0, 10),

    (-5, 0),
    (-6, -1),
    
    (-6, -1),
    (-7, 0),
    (-7, -2),
    (-5, -2),
    (-6, -1),

]

codes = [
    Path.MOVETO, #begin drawing
    Path.LINETO, 
    Path.LINETO, 
    Path.LINETO,
    Path.LINETO, 
    Path.LINETO, 
    Path.LINETO,

    Path.MOVETO, 
    Path.LINETO,
    Path.MOVETO, 
    Path.LINETO,
    Path.LINETO,
    Path.LINETO,
    Path.LINETO, #close shape. This is not required for this shape but is "good form"

]

pth = Path(verts, codes)
pth.vertices[:,1] = pth.vertices[:,1]-5
pth.vertices[:,0] = pth.vertices[:,0]#-5
pth.vertices = pth.vertices/10
air_R_msk_NR = pth

## ##################################
## AIR LEFT MASKED
verts = [
    (0, 0),
    (5, 0),
    (5, 10),
    (-5, 10),
    (-5, 0),
    (0, 0),

    (-5,0),
    (-5, 10),
    (5, 10),
    (5,0),
    (0,0),

]

codes = [
    Path.MOVETO, #begin drawing
    Path.LINETO, 
    Path.LINETO, 
    Path.LINETO,
    Path.LINETO,
    Path.LINETO,

    Path.LINETO, 
    Path.LINETO, 
    Path.LINETO,
    Path.LINETO,
    Path.LINETO, 

]

pth = Path(verts, codes)
pth.vertices[:,1] = pth.vertices[:,1]-5
pth.vertices[:,0] = pth.vertices[:,0]#-5
pth.vertices = pth.vertices/10
air_L_msk = pth

## ##################################
## AIR LEFT MASKED NO RESPONSE
verts = [
    (0, 0),
    (5, 0),
    (5, 10),
    (-5, 10),
    (-5, 0),
    (0, 0),

    (-5,0),
    (-5, 10),
    (5, 10),
    (5,0),
    (0,0),

    (5, 0),
    (6, -1),
    (6, -1),
    (7, 0),
    (7, -2),
    (5, -2),
    (6, -1),

]

codes = [
    Path.MOVETO, #begin drawing
    Path.LINETO, 
    Path.LINETO, 
    Path.LINETO,
    Path.LINETO,
    Path.LINETO,

    Path.LINETO, 
    Path.LINETO, 
    Path.LINETO,
    Path.LINETO,
    Path.LINETO,

    Path.MOVETO, 
    Path.LINETO,
    Path.MOVETO, 
    Path.LINETO,
    Path.LINETO,
    Path.LINETO,
    Path.LINETO, #close shape. This is not required for this shape but is "good form"

]

pth = Path(verts, codes)
pth.vertices[:,1] = pth.vertices[:,1]-5
pth.vertices[:,0] = pth.vertices[:,0]#-5
pth.vertices = pth.vertices/10
air_L_msk_NR = pth

## ##################################
## AIR RIGHT UNMASKED 

circle = Path.circle(radius=5)
verts = np.concatenate([circle.vertices, circle.vertices[::-1, ...]])
codes = np.concatenate([circle.codes, circle.codes])

pth = Path(verts, codes)

air_R_unm = pth


## ##################################
## AIR RIGHT UNMASKED NO RESPONSE

offs = -3.53553391 #-2.597
offx = 5-3.53553391 #0.5268315399999999
offs = -4.47316846
offx = 5-2.59789935
arr_down_R_vert = [
    (-5+offx, 0+offs),
    (-6+offx, -1+offs),
    (-6+offx, -1+offs),
    (-7+offx, 0+offs),
    (-7+offx, -2+offs),
    (-5+offx, -2+offs),
    (-6+offx, -1+offs),
    ]
arr_down_R_codes = [
    Path.MOVETO, 
    Path.LINETO,
    Path.MOVETO, 
    Path.LINETO,
    Path.LINETO,
    Path.LINETO,
    Path.LINETO, #close shape. This is not required for this shape but is "good form"
                    ]
pth = Path(arr_down_R_vert, arr_down_R_codes)
# pth.vertices[:,1] = pth.vertices[:,1]-5
# pth.vertices[:,0] = pth.vertices[:,0]#-5
# pth.vertices = pth.vertices/10

circle = Path.circle(radius=5)
verts = np.concatenate([circle.vertices, circle.vertices[::-1, ...], pth.vertices])
codes = np.concatenate([circle.codes, circle.codes, pth.codes])

pth = Path(verts, codes)

air_R_unm_NR = pth

## ##################################
## AIR LEFT UNMASKED
verts = [
    (-5, 5),
    (5, -5),
    (-5, -5),
    (5, 5),
]

codes = [
    Path.MOVETO, #begin drawing
    Path.LINETO, 
    Path.MOVETO, 
    Path.LINETO,
]

pth = Path(verts, codes)
# pth.vertices[:,1] = pth.vertices[:,1]-5
# pth.vertices[:,0] = pth.vertices[:,0]#-5
pth.vertices = pth.vertices/10
air_L_unm = pth

## ##################################
## AIR LEFT UNMASKED NO RESPONSE
verts = [
    (-5, 5),
    (5, -5),
    (-5, -5),
    (5, 5),

    (5, -5),
    (6, -6),
    (6, -6),
    (7, -5),
    (7, -7),
    (5, -7),
    (6, -6),
]

codes = [
    Path.MOVETO, #begin drawing
    Path.LINETO, 
    Path.MOVETO, 
    Path.LINETO,

    Path.MOVETO, 
    Path.LINETO,
    Path.MOVETO, 
    Path.LINETO,
    Path.LINETO,
    Path.LINETO,
    Path.LINETO, #close shape. This is not required for this shape but is "good form"
]

pth = Path(verts, codes)
# pth.vertices[:,1] = pth.vertices[:,1]-5
# pth.vertices[:,0] = pth.vertices[:,0]#-5
pth.vertices = pth.vertices/10
air_L_unm_NR = pth

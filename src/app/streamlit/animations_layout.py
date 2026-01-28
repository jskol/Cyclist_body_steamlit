import sys,os
import numpy as np
from numpy.typing import NDArray

sys.path.append(os.path.join(os.getcwd(),'src'))
from app.human_body.human_body_2d import Human2D
def genearte_layout_dict(cyclist:Human2D,seat_loc:NDArray)->dict[str, bool| list[float]|int|str]:
    
    bike_x,bike_y=cyclist.bike.plot_bike_plotly(seat_loc)
    #make the x_range span from fron wheel to rearwheel
    x_arr=np.array(list(filter(lambda x: x is not None, bike_x))) #Remove Nones
    y_arr=np.array(list(filter(lambda x: x is not None, bike_y))) #Remove Nones
    x_max=np.amax(x_arr)
    x_min=np.amin(x_arr)
    y_min=np.amin(y_arr)

    
    return {
        "plot_bgcolor":"#FBFAFA",
        "showlegend":False,
        "xaxis": dict(
            range=[x_min-10,x_max+10], 
            autorange=False, 
            showgrid=False,
            fixedrange=True,
            visible=False), #will be updates
        "yaxis":dict(
            range=[y_min*1.01, np.amax([cyclist.shoulder[1],cyclist.hip[1]])+100], 
            autorange=False, 
            showgrid=False,
            scaleanchor="x",
            scaleratio=1,
            fixedrange=True,
            visible=False)
    }

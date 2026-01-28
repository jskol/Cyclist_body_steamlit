import streamlit as st
import sys,os,time
import numpy as np
from numpy.typing import NDArray
import plotly.graph_objects as go
sys.path.append(os.path.join(os.getcwd(),'src'))
from app.human_body.human_body_2d import Human2D

# CREATE layout feautres common for all figures
from app.streamlit.animations_layout import genearte_layout_dict 

def create_SVG_path(Lower_arm:NDArray, Apex:NDArray, Upper_arm:NDArray,flip:bool=False)->str:
    '''
    According to GeminAI its better to approximate an arc 
    by a set of straight lines
    '''
    UA=Upper_arm-Apex
    LA=Lower_arm-Apex
    UA_len=np.linalg.norm(UA)
    LA_len=np.linalg.norm(LA)
    arm=0.35*np.amin([LA_len,UA_len])
    ang_init=np.arctan2(LA[1],LA[0])
    ang_fin=np.arctan2(UA[1],UA[0])
    if flip:
        ang_fin+= 2*np.pi
    diff=ang_fin-ang_init
    #pick the shorter path
    diff = (diff + np.pi) % (2 * np.pi) - np.pi

    angles=np.linspace(ang_init,ang_init+diff,15)
    x=Apex[0]+arm*np.cos(angles)
    y=Apex[1]+arm*np.sin(angles)

    path=f"M {Apex[0]},{Apex[1]} L {x[0]},{y[0]}"
    for x_v,y_v in zip(x[1:],y[1:]):    
        path += f'L {x_v},{y_v} '
    return path + 'Z',(diff*180/np.pi)

from typing import Any
def create_angle_areas(cyclist:Human2D,show_angles:bool)->list[Any]:
    '''
    Creates coloured areas of join angles with
    color depending on the range of motion, if show_angles is False
    then it returns an empty list
    '''
    def allowed_range(range_list:list[float],val:float):
        '''
        Helper function to highlight
        angle out of allowed range
        '''
        if val <= range_list[1] and val >= range_list[0]:
            return "Green"
        else:
            return "Red"
            

    knee_params=create_SVG_path(cyclist.ankle,cyclist.knee,cyclist.hip,cyclist.bike.side=='R')
    hip_params=create_SVG_path(cyclist.knee,cyclist.hip,cyclist.shoulder,cyclist.bike.side !='R') #Has to be opposite to knee
        
    if show_angles:
        shapes_set=[
            #knee angle
            {
                "type":"path",
                "path":knee_params[0],
                "fillcolor": allowed_range([68,150],np.abs(knee_params[1])),
                "opacity" : 0.5,
                "line":{"color":allowed_range([68,150],np.abs(knee_params[1]))}
            },
            #hip angle
            {
                "type":"path",
                "path":hip_params[0],
                "fillcolor": allowed_range([40,180],np.abs(hip_params[1])),
                "opacity" : 0.5,
                "line":{"color":allowed_range([40,180],np.abs(hip_params[1]))}
            }
        ]
        
    else:
        shapes_set=[]
    
    return \
        shapes_set,dict(
            Hip= [np.abs(hip_params[1]),cyclist.hip],
            Knee= [np.abs(knee_params[1]),cyclist.knee]
        )
def create_annotations_list(informations: dict[str,float]):
    results=[]
    shift=0
    for k,v in informations.items():
        results.append(
            go.layout.Annotation(
                x=1., y=1.-shift,
                xref="paper", yref="paper",
                text=f'{k} angle: {v[0]:.2f}',
                showarrow=False,
                font=dict(size=15)
            )
        )
        shift +=0.1
    return results


def animation_native(cyclist:Human2D,current_time:float=0,show_angles:bool=False,number_of_frames:int=60)->None:
    '''
    Main function doing animation
    '''
    #Helper function alert
    def gen_slider_step(frame_name:str):
        '''
        Helper funtion to generate slider steps
        '''
        step={
            "method": "animate",
            "label": frame_name,
            "args": [[frame_name], {
                "mode": "immediate",
                "frame": {"duration": 0, "redraw": True},
            "transition": {"duration": 200}
            }]
        }
        return step
    ##
    
    slider_steps=[]
    frames_dict={}

    for i in range(number_of_frames+1):
        '''
        Generate frames
        '''
        shift_start_ang=np.pi/2 # move by np.pi/2 to start from 12 o'clock
        t = ((i+current_time) / number_of_frames) * 2 * np.pi+shift_start_ang
        frame_name=f'{int(i*360/number_of_frames )}'
        x, y, x_crank,y_crank = cyclist.animation_step_plotly(t) #update moving parts location
        
        shapes_set=create_angle_areas(cyclist,show_angles)
        annotations_list=create_annotations_list(shapes_set[1])
        frames_dict[frame_name]=\
            go.Frame(
                data=[
                    go.Scatter(x=x_crank, y=y_crank, mode="lines+markers",line=dict(color='black')),
                    go.Scatter(x=x, y=y, mode="lines+markers",line=dict(color="#2606F9",width=5))
                ],
                traces=[1,2], #substitute 2nd and 3rd entry (1st one is the bike (fixed) -iniiated before the first frame)
                name=frame_name,
                # Adding angles
                layout=dict(
                    shapes=shapes_set[0],
                    annotations=annotations_list
                )
            )

        #needed for sliders
        slider_steps.append(gen_slider_step(frame_name))
        ## Done

    

    #Get the bike without cranks -> static objects 
    bike_parts_loc=cyclist.bike.get_points_of_contact()
    bike_x,bike_y=cyclist.bike.plot_bike_plotly(bike_parts_loc['seat_loc'])
    bike=[
        go.Scatter(x=bike_x,y=bike_y,mode="lines",line=dict(color='black'))
    ]

    #Common layout features
    frame_layout_common=genearte_layout_dict(cyclist,bike_parts_loc['seat_loc'])

    #add shapes == joint angles if the switch is on
    frame_layout_common["shapes"]=shapes_set[0]
    frame_layout_common["annotations"]=annotations_list
    frame_layout_common["margin"]=dict(t=0)


    # Create initial frame: bike(static) + moving parts (crank + body)
    x_init, y_init,x_crank_init,y_crank_init = cyclist.animation_step_plotly(np.pi/2)
    init_frame_data= bike+[
            go.Scatter(x=x_crank_init, y=y_crank_init, mode="lines+markers",line=dict(color='black')),
            go.Scatter(x=x_init, y=y_init, mode="lines+markers",line=dict(color="#2606F9",width=5),marker=dict(size=10))
            ]

    fig = go.Figure(
        data=init_frame_data,
        layout=go.Layout(
            **frame_layout_common,
            updatemenus=[{ #add buttos to have an animation
                "type": "buttons",
                "direction" :"left",
                "x":0.5,"y":-0.1,
                "bgcolor":"#F30B26",
                "font":{"size":15},
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [10*list(frames_dict.keys()), {
                            "frame": {"duration": 50, "redraw": True},
                            "fromcurrent": True,
                            "transition": {"duration": 0},
                            "loop": True
                        }]
                    },
                    {
                        "label": "Stop",
                        "method": "animate",
                        "args": [
                                [None], 
                                {
                                    "frame": {"duration": 0, "redraw": True}, "mode": "immediate"
                                }
                            ]
                    }
                ]
            }]
        ),
        frames=list(frames_dict.values())
    )
    col1,col2=st.columns([1,1])
    with col1:
        st.plotly_chart(fig)
    with col2: 
        fig_slider=go.Figure(
            data=init_frame_data, 
            layout=go.Layout(
                **frame_layout_common,
                #Add slider functionality
                sliders=[{
                    "active": 0,
                    "currentvalue": {"prefix": "Angle "},
                    "steps": slider_steps
                }]
            ),
            frames=list(frames_dict.values())
        )
        st.plotly_chart(fig_slider)
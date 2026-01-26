import streamlit as st
import sys,os,time
import numpy as np
from numpy.typing import NDArray
import plotly.graph_objects as go
sys.path.append(os.path.join(os.getcwd(),'src'))
from app.human_body.human_body_2d import Human2D

def create_SVG_path(Lower_arm:NDArray, Apex:NDArray, Upper_arm:NDArray,flip:bool=False)->str:
    '''
    According to GeminAI its better to approximat the arc 
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

    angles=np.linspace(ang_init,ang_init+diff,50)
    x=Apex[0]+arm*np.cos(angles)
    y=Apex[1]+arm*np.sin(angles)

    path=f"M {Apex[0]},{Apex[1]} L {x[0]},{y[0]}"
    for x_v,y_v in zip(x[1:],y[1:]):    
        path += f'L {x_v},{y_v} '
    return path + 'Z',(diff*180/np.pi)

from typing import Any
def create_angle_areas(cyclist:Human2D,show_angles:bool)->list[Any]:
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
    hip_params=create_SVG_path(cyclist.knee,cyclist.hip,cyclist.shoulder,cyclist.bike.side=='L')
        
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
    
    return shapes_set

def animation_native(cyclist:Human2D,current_time:float=0,show_angles:bool=False)->None:
    #plot a bike
    bike_x,bike_y=cyclist.bike.plot_bike_plotly(np.array([0.,0.]))
    bike=[
        go.Scatter(x=bike_x,y=bike_y,mode="lines",line=dict(color='black'))
    ]
    
    #make the x_range span from fron wheel to rearwheel
    x_arr=np.array(list(filter(lambda x: x is not None, bike_x))) #Remove Nones
    y_arr=np.array(list(filter(lambda x: x is not None, bike_y))) #Remove Nones
    x_max=np.amax(x_arr)
    x_min=np.amin(x_arr)
    y_min=np.amin(y_arr)


    # Common features of the plots layout
    frame_layout_common={
        "plot_bgcolor":"#FBFAFA",
        "showlegend":False,
        "xaxis": dict(
            range=[], 
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

    frames_count = 60
    frames = []
    frames_name=[]
    slider_steps=[]
    def gen_slider_step(frame_name:str):
        '''
        Helper funtion to generate slider steps
        '''
        step={
            "method": "animate",
            "label": frame_name,
            "args": [[frame_name], {
                "mode": "immediate",
                "frame": {"duration": 0, "redraw": False},
            "transition": {"duration": 200}
            }]
        }
        return step
    
    for i in range(frames_count+1):
        '''
        Generate frames
        '''
        t = ((i+current_time) / frames_count) * 2 * np.pi+np.pi/2
        frames_name.append(f'{int((t-np.pi/2)*360/(2*np.pi) )}')
        x, y, x_crank,y_crank = cyclist.animation_step_plotly(t)
        #Plotting angles
        
        shapes_set=create_angle_areas(cyclist,show_angles)
        frames.append(
            go.Frame(
                data=[
                    go.Scatter(x=x_crank, y=y_crank, mode="lines+markers",line=dict(color='black')),
                    go.Scatter(x=x, y=y, mode="lines+markers",line=dict(color="#2606F9",width=5))
                ],
                traces=[1,2], #substitute 2nd and 3rd entry (1st one is the bike (fixed))
                name=frames_name[-1],
                # Adding angles
                layout=go.Layout(
                    shapes=shapes_set#
                )
            )
        )
        #needed for sliders
        slider_steps.append(gen_slider_step(frames_name[-1]))
        ## Done

    
    #add shapes == joint angles if the switch is on
    frame_layout_common["shapes"]=shapes_set
    #reset the x-axis range
    frame_layout_common['xaxis']['range']=[x_min-10,x_max+10]


    # Create initial frame
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
                        "args": [frames_name*10, {
                            "frame": {"duration": 50, "redraw": True},
                            "fromcurrent": True,
                            "transition": {"duration": 0},
                            "loop": True
                        }]
                    },
                    {
                        "label": "Stop",
                        "method": "animate",
                        "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]
                    }
                ]
            }]
        ),
        frames=frames
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
            frames=frames
        )
        st.plotly_chart(fig_slider)
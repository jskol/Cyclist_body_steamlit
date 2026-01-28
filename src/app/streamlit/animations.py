import streamlit as st
import sys,os,time
import numpy as np
from numpy.typing import NDArray
import plotly.graph_objects as go
sys.path.append(os.path.join(os.getcwd(),'src'))
from app.human_body.human_body_2d import Human2D

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
def create_angle_areas(cyclist:Human2D,show_angles:bool)->tuple[list[Any],dict[str,list[float,NDArray]]]:
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
    
    frames_count = 50
    frames = []
    frames_name=[]
    slider_steps=[]
    for i in range(frames_count):
        t = ((i+current_time) / frames_count) * 2 * np.pi
        frames_name.append(f'T={t}')
        x, y, x_crank,y_crank = cyclist.animation_step_plotly(t)
        #Plotting angles
        
        shapes_set=create_angle_areas(cyclist,show_angles)
        annotions_list=create_annotations_list(shapes_set[1])
        frames.append(
            go.Frame(
                data=[
                    go.Scatter(x=x_crank, y=y_crank, mode="lines+markers",line=dict(color='black')),
                    go.Scatter(x=x, y=y, mode="lines+markers",line=dict(color="#2606F9",width=5))
                ],
                traces=[1,2], #substitute 2nd and 3rd entry (1st one is the bike (fixed))
                name=frames_name[-1],
                # Adding angles
                layout=dict(
                    shapes=shapes_set[0],
                    annotations=annotions_list
                )
            )
        )
        #needed for sliders
        step = {
            "method": "animate",
            "label": f"{i}",
            "args": [[frames_name[-1]], {
                "mode": "immediate",
                "frame": {"duration": 0, "redraw": True},
            "transition": {"duration": 0}
            }]
        }
        slider_steps.append(step)
        ## Done

    x_init, y_init,x_crank_init,y_crank_init = cyclist.animation_step_plotly(0)
    shapes_set=create_angle_areas(cyclist,show_angles)
    annotations_set=create_annotations_list(shapes_set[1])
    xrange=[x_min-10,x_max+10]
    fig = go.Figure(
        data=bike+[
            go.Scatter(x=x_crank_init, y=y_crank_init, mode="lines+markers",line=dict(color='black')),
            go.Scatter(x=x_init, y=y_init, mode="lines+markers",line=dict(color="#2606F9",width=5),marker=dict(size=10))
            ], 
        layout=go.Layout(
            shapes=shapes_set[0],
            annotations=annotations_set,
            plot_bgcolor="#FBFAFA",
            showlegend=False,
            xaxis=dict(range=xrange, autorange=False, showgrid=False,fixedrange=True,visible=False),
            yaxis=dict(range=[y_min*1.01,np.amax([cyclist.shoulder[1],cyclist.hip[1]])+100],
                        autorange=False, showgrid=False,scaleanchor="x",scaleratio=1,fixedrange=True,visible=False),
            updatemenus=[{
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
            data=bike+[
                go.Scatter(x=x_crank_init, y=y_crank_init, mode="lines+markers",line=dict(color='black')),
                go.Scatter(x=x_init, y=y_init, mode="lines+markers",line=dict(color="#2606F9",width=5),marker=dict(size=10))
                ], 
            layout=go.Layout(
                shapes=shapes_set[0],
                annotations=annotations_set,
                plot_bgcolor="#FBFAFA",
                showlegend=False,
                xaxis=dict(range=xrange, autorange=False, showgrid=False,fixedrange=True,visible=False),
                yaxis=dict(range=[y_min*1.01, np.amax([cyclist.shoulder[1],cyclist.hip[1]])+100], autorange=False, showgrid=False,scaleanchor="x",scaleratio=1,fixedrange=True,visible=False),
                sliders=[{
                    "active": 0,
                    "currentvalue": {"prefix": "Time stamp"},
                    "steps": slider_steps
                }]
            ),
            frames=frames
        )
        st.plotly_chart(fig_slider)
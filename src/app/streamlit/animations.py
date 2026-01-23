import streamlit as st
import sys,os,time
import numpy as np
import plotly.graph_objects as go
sys.path.append(os.path.join(os.getcwd(),'src'))
from app.human_body.human_body_2d import Human2D

def animation_native(cyclist:Human2D,current_time:float=0)->None:
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
        frames.append(
            go.Frame(data=[
                go.Scatter(x=x_crank, y=y_crank, mode="lines+markers",line=dict(color='black')),
                go.Scatter(x=x, y=y, mode="lines+markers",line=dict(color="#2606F9",width=5))
            ],
            traces=[1,2], #substitute 2nd and 3rd entry (1st one is the bike (fixed))
            name=frames_name[-1])
            )
        #needed for sliders
        step = {
            "method": "animate",
            "label": f"{i}",
            "args": [[frames_name[-1]], {
                "mode": "immediate",
                "frame": {"duration": 0, "redraw": False},
            "transition": {"duration": 0}
            }]
        }
        slider_steps.append(step)
        ## Done

    x_init, y_init,x_crank_init,y_crank_init = cyclist.animation_step_plotly(0)
    xrange=[x_min-10,x_max+10]
    fig = go.Figure(
        data=bike+[
            go.Scatter(x=x_crank_init, y=y_crank_init, mode="lines+markers",line=dict(color='black')),
            go.Scatter(x=x_init, y=y_init, mode="lines+markers",line=dict(color="#2606F9",width=5),marker=dict(size=10))
            ], 
        layout=go.Layout(
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
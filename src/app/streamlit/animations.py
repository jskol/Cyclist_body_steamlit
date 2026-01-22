import streamlit as st
import sys,os,time
import numpy as np
import plotly.graph_objects as go
sys.path.append(os.path.join(os.getcwd(),'src'))
from app.human_body.human_body_2d import Human2D

def animation_refresh(cyclist:Human2D)->None:
    run_anim = st.toggle("Start pedalling", value=True)
    if 't' not in st.session_state:
        st.session_state.t = 0

    placeholder=st.empty()
    x, y,_,_ = cyclist.animation_step_plotly(0)
    time_step=0.1
    while True:
        if run_anim:
            st.session_state.t += time_step
            t = st.session_state.t*2*np.pi*time_step
            x, y,_,_ = cyclist.animation_step_plotly(t)

        fig = go.Figure(
            go.Scatter(x=x, y=y, mode="lines+markers", line=dict(color="#1404F7", width=5))
            ,layout=go.Layout(
                plot_bgcolor="#FBFAFA"
                )
            )
        fig.update_layout(
            xaxis=dict(range=[-800, 400],showgrid=False),
            yaxis=dict(range=[-1000, 400],showgrid=False,scaleanchor="x",scaleratio=1),
            height=800)
        
        # Wyświetlamy
        placeholder.plotly_chart(fig, width='content', key="Pedalling stick figure",config={'displayModeBar': False})
        time.sleep(0.01)


def animation_native(cyclist:Human2D,current_time:float=0)->None:
    #plot a bike
    bike_x,bike_y=cyclist.bike.plot_bike_plotly(cyclist.hip)
    bike=[
        go.Scatter(x=bike_x,y=bike_y,mode="lines",line=dict(color='black'))
    ]
    
    
    frames_count = 50
    frames = []
    frames_name=[]
    for i in range(frames_count):
        t = ((i+current_time) / frames_count) * 2 * np.pi
        x, y, x_crank,y_crank = cyclist.animation_step_plotly(t)
        frames_name.append(f'T={t}')
        frames.append(
            go.Frame(data=[
                go.Scatter(x=x_crank, y=y_crank, mode="lines+markers",line=dict(color='black')),
                go.Scatter(x=x, y=y, mode="lines+markers",line=dict(color="#2606F9"))
            ],
            traces=[1,2], #substitute 2nd and 3rd entry (1st one is the bike (fixed))
            name=frames_name[-1])
            )

    x_init, y_init,x_crank_init,y_crank_init = cyclist.animation_step_plotly(0)
    xrange=[-800, 400]
    if cyclist.bike.side=='R':
        xrange=[-1*x for x in xrange[::-1]]
    fig = go.Figure(
        data=bike+[
            go.Scatter(x=x_crank_init, y=y_crank_init, mode="lines+markers",line=dict(color='black')),
            go.Scatter(x=x_init, y=y_init, mode="lines+markers",line=dict(color="#2606F9"))
            ], 
        layout=go.Layout(
            plot_bgcolor="#FBFAFA",
            xaxis=dict(range=xrange, autorange=False, showgrid=False,fixedrange=True),
            yaxis=dict(range=[-1000, cyclist.shoulder[1]*1.1], autorange=False, showgrid=False,scaleanchor="x",scaleratio=1,fixedrange=True),
            updatemenus=[{
                "type": "buttons",
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
    st.plotly_chart(fig)#,width='content')




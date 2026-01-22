import streamlit as st
import numpy as np
import os,sys,time

sys.path.append(os.path.join(os.getcwd(),'src'))
from app.human_body.human_body_2d import Human2D
from app.human_body.bike_class import Bike
from app.streamlit.animations import animation_refresh, animation_native

import plotly.graph_objects as go

# Define sidebar 
body_ponts=['torso_len','arm_len','u_leg_len','l_leg_len']
body_dict={}

with st.sidebar :
    st.title('Body geometry')
    for POI in body_ponts:
        slider=st.select_slider(f'Set your {POI}',options=[300+x for x in np.arange(0,700,5)],value=500)
        st.write(f'{POI} is {slider}')
        body_dict[POI]=slider

    #foot setup
    foot_size=st.select_slider(f'Set your foot lenght',options=[200+x for x in np.arange(0,200,5)],value=300)
    st.write(f'Foot lenght set to {foot_size}')
    foot_ang=st.select_slider(f'Set your angle',options=[x for x in np.arange(-30,45,5)],value=15)
    st.write(f'Foot angle set to {foot_ang}')
    cleat_SB=st.select_slider(f'Set your cleat setback',options=[x for x in np.arange(0,foot_size,foot_size/30)],value=foot_size/3)
    st.write(f'Cleat setback set to {foot_size}')

    #hip
    move_hips=st.select_slider(f'saddle set_back',options=[x for x in np.arange(-150,150,5)],value=0)


    st.title('Bike geometry')
    #TODO

#main page

st.title('Bikefit symulator')
animation_description=st.text(f'Descritpion here -> TODO')
swith_sides = st.toggle("Swith sides", key='side_swich',value=False)

bike=Bike()
bike.speacers=30
bike.stem_len=170
bike.stem_angle=-17
bike.side='L'

if swith_sides:
    bike.side='R'

cyclist=Human2D(
    **body_dict,
    bike=bike,
    foot_len=foot_size,
    foot_angle=foot_ang,
    cleat_set_back=cleat_SB
    )

#Sets the Frame of reference
cyclist.update_hip(np.array([move_hips,0]))
POC_dict=bike.get_points_of_contact(np.zeros(2)) #fix the seat a (0.,0.) #cyclist.hip)
st.text(f'bb location is {POC_dict['bb_loc']} ')
# sets the initial positions
foot_on_the_pedal=POC_dict['bb_loc']
foot_on_the_pedal[1]-=bike.crank_len


cyclist.update_foot(foot_on_the_pedal)
cyclist.update_wrist(POC_dict['hoods_loc'])
cyclist.update_knee()
cyclist.update_shoulder()


#animation_refresh(cyclist,run_anim)
animation_native(cyclist)
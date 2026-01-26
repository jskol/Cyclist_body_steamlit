import streamlit as st
import numpy as np
import os,sys,time

sys.path.append(os.path.join(os.getcwd(),'src'))
from app.human_body.human_body_2d import Human2D
from app.human_body.bike_class import Bike
from app.streamlit.animations import animation_native

import plotly.graph_objects as go
#lets try a 3 column structure
st.set_page_config(layout="wide")
body_geo,animation,bike_geo=st.columns([0.2,0.6,0.2])


# A helper dict for body parts
body_points={
    'torso_len': ['Torso length [mm]',np.arange(200,1000,5),500],
    'u_arm_len':['Upper Arm lenght[mm]',np.arange(100,500,5),250],
    'l_arm_len':['Lower Arm lenght [mm]',np.arange(100,500,5),250],
    'u_leg_len':['Upper leg lenght [mm]',np.arange(200,1000,5),400],
    'l_leg_len':['Lower leg lenght [mm]',np.arange(200,1000,5),450],
    'foot_len':['Foot length [mm]',np.arange(200,500,5),285],
    'elbow_bend':['Elbow bend [deg]',np.arange(0,120,1),0],
    'foot_angle':['Foot angle [deg]', np.arange(-45,45,1),15],
}
# Define body geometry from sliders 
with body_geo:
    body_dict={}
    st.header('Body geometry')
    with st.expander('Body dimensions'):
        for POI,vals in list(body_points.items())[:-2]:
            slider=st.select_slider(vals[0],options=[x for x in vals[1]],value=vals[2])
            body_dict[POI]=slider
        #For testing add arm_len
        #body_dict['arm_len']=body_dict['u_arm_len']+body_dict['l_arm_len']
        ##
    for POI,vals in list(body_points.items())[-2:]:
        slider=st.select_slider(vals[0],options=[x for x in vals[1]],value=vals[2])
        body_dict[POI]=slider
    foot_size=body_dict['foot_len']
    cleat_SB=st.select_slider(f'Set your cleat setback [mm]',options=[x for x in np.arange(0,foot_size,1)],value=np.floor(foot_size/3))
    body_dict['cleat_set_back']=cleat_SB

# A helper dict for bike parts
bike_parts={
    'saddle_height': ['Saddle height [mm]',np.arange(600,850,1),750],
    'stem_len':['Stem length [mm]',np.arange(80,170,5),100],
    'stem_angle':['Stem angle [mm]',np.arange(-25,25,1),-12 ],
    'speacers':['Stem specers [mm]',np.arange(0,35,5),0],
    'crank_len':['Crank lenght [mm]',[160,165,167.5,170,172.5,175],165]
}
frame_geometry={
    'seat_tube_angle':['Seat tube angle [deg]',np.arange(70,80,0.5),73.5],
    'head_tube_angle':['Head tube angle [deg]', np.arange(70,80,0.5),73.5],
    'wheel_diameter':['Wheel diameter [mm]', np.arange(600,800,50),700],
    'wheel_base':['Wheel base [mm]',np.arange(800,1200,1),991],
    'bb_drop':['BB drop [mm]', np.arange(-20,100,1),72],
    'head_tube_len':['Head tube lenght [mm]',np.arange(20,220,2),170],
    'seat_tube_len':['Seattube lenght [mm]', np.arange(300,800,1),501]
}
frame_geometry_dict={}


with bike_geo:
    st.header('Bike geometry')
    
    with st.expander('Adjust Frame Geometry'):
        for k,v in frame_geometry.items():
            slider=st.select_slider(v[0],options=[x for x in v[1]],value=v[2])
            frame_geometry_dict[k]=slider
        wheel_size=0.5*frame_geometry_dict['wheel_diameter']
        slider=st.select_slider('Frame stack height',options=[x for x in np.arange(wheel_size,2*wheel_size)],value=555)
        frame_geometry_dict['stack']=slider
        slider=st.select_slider('Fork lenght',options=[x for x in np.arange(wheel_size,frame_geometry_dict['stack'])],value=358)
        frame_geometry_dict['fork_len']=slider
    

    
    bike_geo_dict={}
    for k,v in bike_parts.items():
        slider=st.select_slider(v[0],options=[x for x in v[1]],value=v[2])
        bike_geo_dict[k]=slider
    
    #The trick is to move human not bike
    move_hips=st.select_slider(f'Saddle setback [mm]',options=[x for x in np.arange(-150,150,5)],value=0) 


#animation page
with animation:
    
    st.title('Bikefit symulator') 
    #Initialize the bike and the rider
    bike=Bike(**bike_geo_dict,**frame_geometry_dict)
    bike.side='L'

    
    switch_1,switch_2=st.columns([0.5,0.5])
    with switch_1:
        swith_sides = st.toggle("Swith sides", key='side_swich',value=False)
        if swith_sides:
            bike.side='R'
    with switch_2:
        plot_angles=st.toggle("Show angles",key='Show angles',value=False)

    try:
        cyclist=Human2D(
            **body_dict,
            bike=bike,
            )

        #Sets the Frame of reference and sat up the rider on a bike
        #st.text(f'bb location is {POC_dict['bb_loc']} ')
        POC_dict=bike.get_points_of_contact(np.zeros(2)) #fix the seat a (0.,0.) #cyclist.hip)
        cyclist.update_hip(POC_dict['seat_loc']+np.array([move_hips,0.]))

        # sets the initial positions
        foot_on_the_pedal=POC_dict['bb_loc']
        foot_on_the_pedal[1]-=bike.crank_len
        cyclist.update_foot(foot_on_the_pedal)
        cyclist.update_wrist(POC_dict['hoods_loc'])

        cyclist.update_knee()
        cyclist.update_shoulder()


        #animation_refresh(cyclist,run_anim)
        animation_native(cyclist,show_angles=plot_angles)
    except Exception as e:
        st.text(f'Impossible fit due to {e}')    

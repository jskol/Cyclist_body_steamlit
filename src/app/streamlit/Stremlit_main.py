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
st.markdown("<h1 style='text-align: center;'>Bikefit simulator</h1>", unsafe_allow_html=True)
body_geo,animation,bike_geo=st.columns([0.2,0.6,0.2],border=True)


# A helper dict for body parts
body_points={
    'torso_len': ['Torso length [mm]',np.arange(200,1000,5),500,None],
    'u_arm_len':['Upper Arm lenght[mm]',np.arange(100,500,5),250,None],
    'l_arm_len':['Lower Arm lenght [mm]',np.arange(100,500,5),250,None],
    'u_leg_len':['Upper leg lenght [mm]',np.arange(200,1000,5),420,None],
    'l_leg_len':['Lower leg lenght [mm]',np.arange(200,1000,5),400,None],
    'foot_len':['Foot length [mm]',np.arange(200,500,5),285,None],
    'ankle_height':['Foot height [mm]', np.arange(10,150,1),50,
                    'Distance from the ground to the ankle'],
    'elbow_bend':['Elbow bend [deg]',np.arange(0,120,1),0,
                  '0 angle means arms are fully extended'],
    'foot_angle':['Foot angle [deg]', np.arange(-45,45,1),15,
                  "Angle your foot makes with the ground\
                      when the pedal is at 6 o' clock"
                    ],
    'ankle_mobility':[f'Set your ankling range +- [deg]',
                    np.arange(0,45,1),5,
                    'Maximal angular deviation (in deg)\n \
                    from your ankle angle at the bottom\
                    of the pedal stroke']
    
}
# Define body geometry from sliders 
with body_geo:
    body_dict={}
    st.header('Body geometry')
    with st.expander('Body dimensions'):
        for POI,vals in list(body_points.items())[:-3]:
            slider=st.select_slider(
                    vals[0],
                    options=[x for x in vals[1]],
                    value=vals[2],
                    help=vals[3]
                )
            body_dict[POI]=slider

    for POI,vals in list(body_points.items())[-3:]:
        slider=st.select_slider(
                    vals[0],
                    options=[x for x in vals[1]],
                    value=vals[2],
                    help=vals[3]
            )
        body_dict[POI]=slider
    
    foot_size=body_dict['foot_len']
    cleat_SB=st.select_slider(
        f'Set your cleat setback [mm]',
        options=[x for x in np.arange(0,foot_size,1)],
        value=np.floor(foot_size/3),
        help='Measured from toes to the center of the cleat'
        )
    body_dict['cleat_set_back']=cleat_SB

# A helper dict for bike parts

 
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
        link_to_geo_charts='https://geometrygeeks.bike/'
        st.markdown(f"Details of your bike can be (probably) found at [here]({link_to_geo_charts}) ")
        for k,v in frame_geometry.items():
            slider=st.select_slider(v[0],options=[x for x in v[1]],value=v[2])
            frame_geometry_dict[k]=slider
        wheel_size=0.5*frame_geometry_dict['wheel_diameter']
        slider=st.select_slider('Frame stack height',options=[x for x in np.arange(wheel_size,2*wheel_size)],value=555)
        frame_geometry_dict['stack']=slider
        slider=st.select_slider('Fork lenght',options=[x for x in np.arange(wheel_size,frame_geometry_dict['stack'])],value=358)
        frame_geometry_dict['fork_len']=slider
    

    
    bike_geo_dict={}
    
    with st.expander('Seat setup'):
    #The trick is to move human not bike
        bike_geo_dict['saddle_height']=st.select_slider(
            'Saddle height [mm]',
            options=np.arange(600,850,1),
            value=750
        )
        bike_geo_dict['saddle_lenght']=st.select_slider(
            'Saddle length',
            options=np.arange(120,300,5),
            value=150
        )
        sd_len=bike_geo_dict['saddle_lenght']
        bike_geo_dict['saddle_tilt']=st.select_slider(
            'Saddle tilt [deg]',
            options=np.arange(-20,20,1),
            value=0
        )
        sd_range=np.linspace(-0.5*sd_len,0.5*sd_len,20)
        move_hips=st.select_slider(
            f'Setback [mm]',
            options=[x for x in sd_range],
            value=sd_range[len(sd_range)//2],
            format_func= lambda x: f'{x:.2f}'
            )
        bike_geo_dict['saddle_set_back']=move_hips

    with st.expander('Cockpit'):
        cockpit_dict={
            'stem_len':['Stem length [mm]',np.arange(80,170,5),100],
            'stem_angle':['Stem angle [mm]',np.arange(-25,25,1),-12 ],
            'speacers':['Stem specers [mm]',np.arange(0,35,5),0]
        }
        for k,v in cockpit_dict.items():
            bike_geo_dict[k]=st.select_slider(v[0],options=[x for x in v[1]],value=v[2])
            
    with st.expander('Cranks'):    
        bike_geo_dict['crank_len']=st.select_slider(
        'Crank lenght [mm]',
        options=[160,165,167.5,170,172.5,175],
        value=165
        )





#animation page
with animation:
    
   
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
        POC_dict=bike.get_points_of_contact(np.zeros(2)) #fix the seat a (0.,0.) #cyclist.hip)
        #seat_angle
        seat_angle_temp=cyclist.bike.saddle_tilt*np.pi/180
        sign=cyclist.bike.side_to_sign()
        cyclist.update_hip(
            POC_dict['seat_loc']\
                +np.array([
                    -sign*move_hips*np.cos(seat_angle_temp),
                    -move_hips*np.sin(seat_angle_temp)
                    ]))

        # sets the initial positions
        foot_on_the_pedal=POC_dict['bb_loc']
        foot_on_the_pedal[1]-=bike.crank_len
        cyclist.update_foot(foot_on_the_pedal)
        cyclist.update_wrist(POC_dict['hoods_loc'])

        cyclist.update_knee()
        cyclist.update_shoulder()


        #Define colorsceme of the plot
        from app.streamlit.animation_details_class import AnimationSettings
        animation_settings=AnimationSettings(show_angles=plot_angles)

        animation_native(cyclist,animation_settings)
    except Exception as e:
        st.text(f'Impossible fit due to {e}')    

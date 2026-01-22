import matplotlib.pyplot as plt
import numpy as np

from app.human_body.human_body_2d import Human2D
from app.human_body.bike_class import Bike
from matplotlib.animation import FuncAnimation


if __name__=="__main__":
    bike=Bike()
    bike.speacers=30
    bike.stem_len=170
    bike.stem_angle=-17
    bike.side='L'
    cyclist=Human2D(
        arm_len=600,
        torso_len=500,
        u_leg_len=500,
        l_leg_len=500,
        bike=bike,
        foot_len=286,
        foot_angle=15,
        cleat_set_back=150
        )
    
    #Sets the Frame of reference
    cyclist.update_hip(np.array([0,0]))
    POC_dict=bike.get_points_of_contact(cyclist.hip)
    
    # sets the initial positions
    foot_on_the_pedal=POC_dict['bb_loc']
    foot_on_the_pedal[1]-=bike.crank_len
   
    
    cyclist.update_foot(foot_on_the_pedal)
    cyclist.update_wrist(POC_dict['hoods_loc'])
    cyclist.update_knee()
    cyclist.update_shoulder()

    #Set-up plotting 
    fig,ax=plt.subplots()
    ax.set_xlim(-1200,800)
    ax.set_ylim(-1200,800)
    ax.set_aspect('equal')
    #initialize animation
    cyclist.setup_plot(ax,col='red')
    anim=FuncAnimation(fig,cyclist.animation_step,frames=500,interval=150,blit=True)
    
    plt.show()



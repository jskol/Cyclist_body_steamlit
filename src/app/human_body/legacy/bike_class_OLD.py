import matplotlib.pyplot as plt
from numpy.typing import NDArray
import numpy as np


def plot_bike(self,ax,saddle_loc:NDArray=np.array([0,0])):
        
        common={'color':'k','linewidth': 3,}
        sign=self.side_to_sign()
        POC_dict=self.get_points_of_contact(saddle_loc) #Calculate location of POC
        bb_loc=POC_dict['bb_loc']

        #bb_loc=self.calc_bb_loc(saddle_loc)
        ax.plot([saddle_loc[0],bb_loc[0]],[saddle_loc[1],bb_loc[1]],**common) # seat_tube
        wheel_y=bb_loc[1]+self.bb_drop
        wheel_x=bb_loc[0]-sign*(60+0.5*self.wheel_diameter)
        front_wheel_x=wheel_x+sign*self.wheel_base
        ax.plot([bb_loc[0],wheel_x],[bb_loc[1],wheel_y],**common) # rear fork (down)
        
        rear_wheel=plt.Circle((wheel_x,wheel_y),0.5*self.wheel_diameter,fill=False,**common)
        ax.add_patch(rear_wheel) #rear_wheel
        
        front_wheel=plt.Circle((front_wheel_x,wheel_y),0.5*self.wheel_diameter,fill=False,**common)
        ax.add_patch(front_wheel) #front_wheel

        steerer=self.calc_steerer_tube_loc(saddle_loc)
        ax.plot(
            [front_wheel_x,steerer[0]],
            [wheel_y,steerer[1]],
            **common     
        ) #fork

        ax.plot(
            [bb_loc[0],front_wheel_x-sign*self.fork_len/np.tan(self.head_tube_angle*np.pi/180)],
            [bb_loc[1],wheel_y+self.fork_len/np.sin(self.head_tube_angle*np.pi/180)],
            **common
        )#bottom tube

        seat_tube_end=np.array([
            bb_loc[0]-sign*self.seat_tube_len*np.cos(self.seat_tube_angle*np.pi/180),
            bb_loc[1]+self.seat_tube_len*np.sin(self.seat_tube_angle*np.pi/180),
        ])
        ax.plot(
            [steerer[0],seat_tube_end[0]],
            [steerer[1],seat_tube_end[1]],
            **common
        )#top_tube

        ax.plot(
            [seat_tube_end[0],wheel_x],
            [seat_tube_end[1],wheel_y],
            **common
        )# Rear top fork
    
        ax.plot(
            [steerer[0],steerer[0]-sign*self.speacers/np.tan(self.head_tube_angle*np.pi/180)],
            [steerer[1],steerer[1]+self.speacers/np.sin(self.head_tube_angle*np.pi/180)],
            color='blue',linewidth=3
        )# Add spacers

        ax.plot(
            [steerer[0]-sign*self.speacers/np.tan(self.head_tube_angle*np.pi/180),\
                POC_dict['hoods_loc'][0]],
            [steerer[1]+self.speacers/np.sin(self.head_tube_angle*np.pi/180),\
                POC_dict['hoods_loc'][1]
                ],
            **common
        )#stem

import numpy as np
import matplotlib.pyplot as plt
from numpy.typing import NDArray
from dataclasses import dataclass
@dataclass
class Bike:
    crank_len:float=165.
    saddle_height:float=750.
    seat_tube_angle:float=73.5
    head_tube_angle:float=73.5
    reach:float=398
    wheel_diameter:float=622
    wheel_base:float=991
    saddle_set_back:float=0
    bb_drop:float=72
    stack:float=555
    head_tube_len:float=170
    fork_len:float=358
    seat_tube_len:float=501
    speacers:float=10
    stem_angle:float=-12
    stem_len:float=110
    side:str='L' # optionally can be right 'R'

    def calc_bb_loc(self,saddle_loc:NDArray=np.array([0,0]))->NDArray:
        '''
        Helper function for calulating bb location realive 
        to the position of the seat
        '''
        sign=-1
        if self.side =='R':
            sign=1

        bb_loc=np.array([
            saddle_loc[0]+sign*self.saddle_height*np.cos(self.seat_tube_angle*np.pi/180),
            saddle_loc[1]-self.saddle_height*np.sin(self.seat_tube_angle*np.pi/180)
        ])
        return bb_loc
    

    def calc_steerer_tube_loc(self,saddle_loc:NDArray=np.array([0,0]))->NDArray:
        '''
        Helper function for calulating location of the steerer 
        w/o the spacers (end of the top bearing of the headset)
        realive to the position of the seat
        '''
        sign=-1
        if self.side =='R':
            sign=1

        bb_loc=self.calc_bb_loc(saddle_loc)
        wheel_y=bb_loc[1]+self.bb_drop
        wheel_x=bb_loc[0]-sign*(60+0.5*self.wheel_diameter)
        wheel_x+=sign*self.wheel_base
        return np.array([
            wheel_x-sign*self.stack/np.tan(self.head_tube_angle*np.pi/180),
            wheel_y+self.stack/np.sin(self.head_tube_angle*np.pi/180)
        ])
    

    def get_points_of_contact(self,seat_loc:NDArray=np.array([0,0]))->dict[str,NDArray]:
        '''
        Function wrapper calculating
        POC-points-of-contact location
        relative to seat_loc
        and returns a dict with 
        *) 'seat_loc' -(x,y) location of the seat
        *) 'bb_loc' -(x,y) location of the bb
        *) 'hoods_loc' -(x,y) location of the hoods
        '''
        
        sign=-1
        if self.side =='R':
            sign=1
        res={}

        res['seat_loc']=seat_loc
        res['bb_loc']=self.calc_bb_loc(res['seat_loc'])
        steerer=self.calc_steerer_tube_loc(res['seat_loc'])
        steerer[0] -= sign*self.speacers/np.tan(self.head_tube_angle*np.pi/180)
        steerer[0] += sign*self.stem_len*np.cos((90-self.head_tube_angle+self.stem_angle)*np.pi/180)
        steerer[1] += self.speacers/np.sin(self.head_tube_angle*np.pi/180)
        steerer[1] += self.stem_len*np.sin((90-self.head_tube_angle+self.stem_angle)*np.pi/180)
        res['hoods_loc']=steerer
        
        return res


    def plot_bike(self,ax,saddle_loc:NDArray=np.array([0,0])):
        
        common={'color':'k','linewidth': 3,}
        sign=-1
        if self.side =='R':
            sign=1
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



if __name__=="__main__":
    fig,ax=plt.subplots()
    bike=Bike()
    bike.plot_bike(ax)
    plt.show()
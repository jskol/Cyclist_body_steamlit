import numpy as np
import matplotlib.pyplot as plt
from numpy.typing import NDArray
from dataclasses import dataclass
import os,sys

curr_dir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(curr_dir)
from .legacy.bike_class_OLD import plot_bike

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
    saddle_lenght:float=180
    saddle_tilt:float=0
    bb_drop:float=72
    stack:float=555
    head_tube_len:float=170
    fork_len:float=358
    seat_tube_len:float=501
    speacers:float=10
    stem_angle:float=-12
    stem_len:float=110
    
    
    side:str='L' # optionally can be right 'R'

    #helper-function for flipping the picture
    def side_to_sign(self)->float:
        if self.side=='L':
            return -1.
        elif self.side=='R':
            return 1.
        else:
            raise ValueError(".side can ONLY be 'L' or 'R' ")


    def calc_bb_loc(self,saddle_loc:NDArray=np.array([0,0]))->NDArray:
        '''
        Helper function for calulating bb location realive 
        to the position of the seat
        '''
        sign=self.side_to_sign()

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
        sign=self.side_to_sign()
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
        
        sign=self.side_to_sign()
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


   
    def plot_bike_plotly(self,saddle_loc:NDArray=np.array([0,0]))->tuple[list[float],list[float]]:
        x,y=[],[]
        sign=self.side_to_sign()
        POC_dict=self.get_points_of_contact(saddle_loc) #Calculate location of POC
        bb_loc=POC_dict['bb_loc']

        #seat-tube
        x.extend([saddle_loc[0],bb_loc[0]])
        y.extend([saddle_loc[1],bb_loc[1]])

        wheel_y=bb_loc[1]+self.bb_drop
        wheel_x=bb_loc[0]-sign*(60+0.5*self.wheel_diameter)
        front_wheel_x=wheel_x+sign*self.wheel_base
        #Wheels
        for wheel_center in [np.array([wheel_x,wheel_y]),np.array([front_wheel_x,wheel_y])]:
            temp_wheel_x=[None]
            temp_wheel_y=[None]
            for ang in np.linspace(0,2*np.pi,num=100):
                temp_wheel_x.append(0.5*self.wheel_diameter*np.cos(ang)+wheel_center[0])
                temp_wheel_y.append(0.5*self.wheel_diameter*np.sin(ang)+wheel_center[1])
            temp_wheel_x.append(None)
            temp_wheel_y.append(None)
            x.extend(temp_wheel_x)
            y.extend(temp_wheel_y)

        #rear-stays
        x.extend([None,bb_loc[0],wheel_x,None])
        y.extend([None,bb_loc[1],wheel_y,None])

        #fork
        steerer=self.calc_steerer_tube_loc(saddle_loc)
        x.extend([front_wheel_x,steerer[0]])
        y.extend([wheel_y,steerer[1]])

        #bottom tube
        x.extend([None,bb_loc[0],front_wheel_x-sign*self.fork_len/np.tan(self.head_tube_angle*np.pi/180),None])
        y.extend([None,bb_loc[1],wheel_y+self.fork_len/np.sin(self.head_tube_angle*np.pi/180),None])

            
        #top_tube
        seat_tube_end=np.array([
            bb_loc[0]-sign*self.seat_tube_len*np.cos(self.seat_tube_angle*np.pi/180),
            bb_loc[1]+self.seat_tube_len*np.sin(self.seat_tube_angle*np.pi/180),
        ])
        x.extend([None,steerer[0],seat_tube_end[0],None]),
        y.extend([None,steerer[1],seat_tube_end[1],None])

        # Rear top fork
        
        x.extend([None,seat_tube_end[0],wheel_x,None])
        y.extend([None,seat_tube_end[1],wheel_y,None])

        #Spacers
        x.extend([None,steerer[0],steerer[0]-sign*self.speacers/np.tan(self.head_tube_angle*np.pi/180),None])
        y.extend([None,steerer[1],steerer[1]+self.speacers/np.sin(self.head_tube_angle*np.pi/180),None])

        #Stem
        x.extend([None,steerer[0]-sign*self.speacers/np.tan(self.head_tube_angle*np.pi/180),\
                POC_dict['hoods_loc'][0],None])
        y.extend([None,steerer[1]+self.speacers/np.sin(self.head_tube_angle*np.pi/180),\
                POC_dict['hoods_loc'][1],None])

        #seat
        seat_temp=0.5*self.saddle_lenght+self.saddle_set_back
        x.extend([None,
                  saddle_loc[0]+sign*(0.5*self.saddle_lenght-self.saddle_set_back)\
                      *np.cos(self.saddle_tilt*np.pi/180),
                  saddle_loc[0]-sign*(0.5*self.saddle_lenght+self.saddle_set_back)
                  *np.cos(self.saddle_tilt*np.pi/180),
                  None
                ])
        y.extend([None,
                  saddle_loc[0]+(0.5*self.saddle_lenght-self.saddle_set_back)\
                      *np.sin(self.saddle_tilt*np.pi/180),
                  saddle_loc[0]-(0.5*self.saddle_lenght+self.saddle_set_back)\
                      *np.sin(self.saddle_tilt*np.pi/180),
                  None
                ])

        return x,y

    #import legacy functionalities for backward compatibility
    plot_bike=plot_bike




if __name__=="__main__":
    fig,ax=plt.subplots()
    bike=Bike()
    bike.plot_bike(ax)
    plt.show()
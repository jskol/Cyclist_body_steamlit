import numpy as np
from numpy.typing import NDArray
from matplotlib.lines import Line2D
from dataclasses import dataclass,field
from app.human_body.bike_class import Bike
@dataclass
class Human2D:
    #joints positions
    # with 3 points of contact fixed
    hip:NDArray=None # Fixed ->saddle
    ankle:NDArray=None #Fixed -> pedal
    wrist:NDArray=None #fixed ->bars
    # Adjustable joints
    knee:NDArray =None
    shoulder:NDArray =None
    #fixed lengts
    arm_len: float =None
    torso_len: float =None
    u_leg_len: float =None
    l_leg_len: float =None
    foot_len:float=None
    foot_angle:float=None
    bike: Bike=field(default_factory=Bike)
    # For animation
    lines:dict[str,list[Line2D]]=field(default_factory= dict)


    # update position of fixed points
    def update_ankle(self, new_pos:NDArray)->None:
        self.ankle=new_pos
    def update_hip(self, new_pos:NDArray)->None:
        self.hip=new_pos
    def update_wrist(self, new_pos:NDArray)->None:
        self.wrist=new_pos

    # Update adjustable joints
    def update_knee(self):
        diff= self.ankle-self.hip # distance between them
        len_diff=np.linalg.norm(diff)

        #if we max out then return leg fully straighten
        #from hip towards the angkle

        if len_diff > (self.l_leg_len+self.u_leg_len):
            self.knee= self.hip +(diff/len_diff)*self.u_leg_len 
        else:
            #use cosine theorem to deal with knee angles
            cos_alpha = (self.u_leg_len**2 + len_diff**2 - self.l_leg_len**2) / (2 * self.u_leg_len*len_diff )
            
            # use clip to avoid floating point errors
            alpha = np.arccos(np.clip(cos_alpha, -1.0, 1.0))
            
            # 3. leg angle
            beta = np.arctan2(diff[1], diff[0])
            
            # 4. pick "physical" knee angle 
            angle = beta + alpha if self.hip[0]<self.ankle[0] else beta - alpha
            
            # 5. Update knee postion
            self.knee = np.array([
                self.hip[0] + self.u_leg_len* np.cos(angle),
                self.hip[1] + self.u_leg_len* np.sin(angle)
            ])   

    def update_shoulder(self):
        diff= self.wrist-self.hip # distance between them
        len_diff=np.linalg.norm(diff)

        #if we max out then return leg fully straighten
        #from hip towards the angkle

        if len_diff > (self.arm_len+self.torso_len):
            self.knee= self.hip +(diff/len_diff)*self.torso_len 
        else:
            #use cosine theorem to deal with knee angles
            cos_alpha = (self.torso_len**2 + len_diff**2 - self.arm_len**2) / (2 * self.torso_len*len_diff )
            
            # use clip to avoid floating point errors
            alpha = np.arccos(np.clip(cos_alpha, -1.0, 1.0))
            
            # 3. leg angle
            beta = np.arctan2(diff[1], diff[0])
            
            # 4. pick "physical" knee angle 
            angle = beta + alpha if self.hip[0]<self.wrist[0] else beta - alpha
            
            # 5. Update shoulder
            self.shoulder = np.array([
                self.hip[0] + self.torso_len* np.cos(angle),
                self.hip[1] + self.torso_len* np.sin(angle)
            ]) 

    #For animations 
    def setup_plot(self, ax,col:str='k'):

        self.bike.plot_bike(ax,self.hip)
        common_style = {'marker': 'o', 'linewidth': 3, 'markersize': 6,'color':col}
        self.lines['crank']     = ax.plot([], [], color='k',linewidth=3)[0]
        self.lines['upper_leg'] = ax.plot([], [], **common_style)[0]
        self.lines['lower_leg'] = ax.plot([], [], **common_style)[0]
        self.lines['torso']     = ax.plot([], [], **common_style)[0]
        self.lines['arm']       = ax.plot([], [], **common_style)[0]


        return self.lines.values()
    

    def start_pedaling(self,frame)->None:
        t = frame / 1.0
        crank_len=self.bike.crank_len
        bb_loc=self.bike.calc_bb_loc(self.hip)
        direction=-1 if self.bike.side=='R' else 1
        self.update_ankle(np.array([
            bb_loc[0] + direction*crank_len * np.cos(t),
            bb_loc[1] + crank_len * np.sin(t)
        ])
        )
        self.update_knee()      

     
    def animation_step(self, frame):
        self.start_pedaling(frame)
        bb_loc=self.bike.calc_bb_loc()
        # Aktualizacja danych w istniejących obiektach linii
        self.lines['crank'].set_data([self.ankle[0],bb_loc[0]],[self.ankle[1],bb_loc[1]])
        self.lines['upper_leg'].set_data([self.hip[0], self.knee[0]], [self.hip[1], self.knee[1]])
        self.lines['lower_leg'].set_data([self.ankle[0], self.knee[0]], [self.ankle[1], self.knee[1]])
        self.lines['torso'].set_data([self.hip[0], self.shoulder[0]], [self.hip[1], self.shoulder[1]])
        self.lines['arm'].set_data([self.wrist[0], self.shoulder[0]], [self.wrist[1], self.shoulder[1]])
        
        return self.lines.values()
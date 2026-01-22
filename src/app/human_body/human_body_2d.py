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
    foot:NDArray=None # Fixed->pedal
    wrist:NDArray=None #fixed ->bars
    
    #Semi-adjustable 
    #important for the knee which is adjusted by hip-ankle position
    ankle:NDArray=None 

    # Adjustable joints
    knee:NDArray =None
    shoulder:NDArray =None
    #fixed lengts
    arm_len: float =None
    
    # for future improvements #
    u_arm_len:float=None
    l_arm_len:float=None
    arm_bend:float=None
    elbow:NDArray=None
    ###########################

    torso_len: float =None
    u_leg_len: float =None
    l_leg_len: float =None
    foot_len:float=None
    foot_angle:float=None
    cleat_set_back:float=0

    bike: Bike=field(default_factory=Bike)
    # For animation
    lines:dict[str,list[Line2D]]=field(default_factory= dict)

    # update position of fixed points
    def update_hip(self, new_pos:NDArray)->None:
        self.hip=new_pos
    def update_wrist(self, new_pos:NDArray)->None:
        self.wrist=new_pos

    def update_foot(self, new_pos:NDArray)->None:
        '''
        new_pos is the position of the pedal spindel
        so one has to include cleat_set back
        '''
        direction=self.bike.side_to_sign()

        self.foot=np.array([
            new_pos[0]+direction*self.cleat_set_back*np.cos(self.foot_angle*np.pi/180.),
            new_pos[1]-self.cleat_set_back*np.sin(self.foot_angle*np.pi/180.)            
        ])
        ankle_pos=np.array([
            new_pos[0]-direction*(self.foot_len-self.cleat_set_back)*np.cos(self.foot_angle*np.pi/180.),
            new_pos[1]+(self.foot_len-self.cleat_set_back)*np.sin(self.foot_angle*np.pi/180.)
        ])
        self.ankle=ankle_pos 

    # Update adjustable joints
    def update_knee(self):
        '''
        update_knee recalulates the position
        of the knee as a result of ankle and
        hip position
        '''
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
            sign=self.bike.side_to_sign()
            angle = beta + sign*alpha #if self.hip[0]<self.ankle[0] else beta - alpha
            
            # 5. Update knee postion
            self.knee = np.array([
                self.hip[0] + self.u_leg_len* np.cos(angle),
                self.hip[1] + self.u_leg_len* np.sin(angle)
            ])   

    def update_shoulder(self):
        '''
        update_shoulder recalculates the postion of the 
        shoulder whihch is determined by the location
        of hips and wrists in space
        '''
        diff= self.wrist-self.hip # distance between them
        len_diff=np.linalg.norm(diff)

        #if we max out then return leg fully straighten
        #from hip towards the angkle

        if len_diff > (self.arm_len+self.torso_len):
            self.shoulder= self.hip +(diff/len_diff)*self.torso_len 
        
        else:
            #use cosine theorem to deal with knee angles
            cos_alpha = (self.torso_len**2 + len_diff**2 - self.arm_len**2) / (2 * self.torso_len*len_diff )
    
            # use clip to avoid floating point errors
            alpha = np.arccos(np.clip(cos_alpha, -1.0, 1.0))
            
            # 3. leg angle
            beta = np.arctan2(diff[1], diff[0])
            
            # 4. pick "physical" shoulder angle --> only plus sign solution

            angle = beta + alpha if self.hip[0]<self.wrist[0] else beta - alpha
            
            # 5. Update shoulder
            self.shoulder = np.array([
                self.hip[0] +self.torso_len* np.cos(angle),
                self.hip[1] + self.torso_len* np.sin(angle)
            ]) 

    #For animations
    def start_pedaling(self,frame)->None:
        '''
        Helper function intoruding dynamics->pedalling
        as a function of frame=time
        '''
        t = frame / 1.0
        crank_len=self.bike.crank_len
        bb_loc=self.bike.calc_bb_loc(self.hip)
        direction=self.bike.side_to_sign()
        self.update_foot(np.array([
            bb_loc[0] - direction*crank_len * np.cos(t),
            bb_loc[1] + crank_len * np.sin(t)
        ])
        )
        self.update_knee()      

    # Initialize the plots 
    def setup_plot_pyplot(self, ax,col:str='k'):
        '''
        Initialize the plotting objects
        '''
        self.bike.plot_bike(ax,self.hip)
        common_style = {'marker': 'o', 'linewidth': 3, 'markersize': 6,'color':col}
        self.lines['crank']     = ax.plot([], [], color='k',linewidth=3)[0]
        self.lines['foot']      = ax.plot([], [], **common_style)[0]
        self.lines['upper_leg'] = ax.plot([], [], **common_style)[0]
        self.lines['lower_leg'] = ax.plot([], [], **common_style)[0]
        self.lines['torso']     = ax.plot([], [], **common_style)[0]
        self.lines['arm']       = ax.plot([], [], **common_style)[0]
        return self.lines.values()
    
    #

    def animation_step_pyplot(self, frame):
        '''
        Plots the current frame
        '''
        #Start the movement
        self.start_pedaling(frame)
        
        # Update positions of "sticks" in the animation
        bb_loc=self.bike.calc_bb_loc()
        # Crak has to go from bb to pedal spindle and not the foot so
        # The cleat set-back has to be included
        direction=self.bike.side_to_sign()
        spindle_loc=np.array([
            self.foot[0]-direction*self.cleat_set_back*np.cos(self.foot_angle*np.pi/180),
            self.foot[1]+self.cleat_set_back*np.sin(self.foot_angle*np.pi/180)
        ])
        self.lines['crank'].set_data([spindle_loc[0],bb_loc[0]],[spindle_loc[1],bb_loc[1]])
        self.lines['upper_leg'].set_data([self.hip[0], self.knee[0]], [self.hip[1], self.knee[1]])
        self.lines['foot'].set_data([self.foot[0],self.ankle[0]],[self.foot[1],self.ankle[1]])
        self.lines['lower_leg'].set_data([self.ankle[0], self.knee[0]], [self.ankle[1], self.knee[1]])
        self.lines['torso'].set_data([self.hip[0], self.shoulder[0]], [self.hip[1], self.shoulder[1]])
        self.lines['arm'].set_data([self.wrist[0], self.shoulder[0]], [self.wrist[1], self.shoulder[1]])
        
        return self.lines.values()
    

    def animation_step_plotly(self, frame)->tuple[list[float],list[float]]:
        '''
        return position of body parts and crankarm
        '''
        x,y=[],[]
        x_crank,y_crank=[],[]
        #Start the movement
        self.start_pedaling(frame)
        
        # Update positions of "sticks" in the animation
        bb_loc=self.bike.calc_bb_loc()
        # Crak has to go from bb to pedal spindle and not the foot so
        # The cleat set-back has to be included
        direction=self.bike.side_to_sign()
        spindle_loc=np.array([
            self.foot[0]-direction*self.cleat_set_back*np.cos(self.foot_angle*np.pi/180),
            self.foot[1]+self.cleat_set_back*np.sin(self.foot_angle*np.pi/180)
        ])
        x.extend([self.foot[0],self.ankle[0],self.knee[0],self.hip[0],self.shoulder[0],self.wrist[0]])
        y.extend([self.foot[1],self.ankle[1],self.knee[1],self.hip[1],self.shoulder[1],self.wrist[1]])
        
        x_crank.extend([spindle_loc[0],bb_loc[0]])
        y_crank.extend([spindle_loc[1],bb_loc[1]])

        return x,y,x_crank,y_crank
import numpy as np
from numpy.typing import NDArray
from matplotlib.lines import Line2D
from dataclasses import dataclass,field
from app.human_body.bike_class import Bike

import os,sys
curr_dir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(curr_dir)
from .legacy.human_body_2d_OLD import setup_plot_pyplot,animation_step_pyplot



@dataclass
class Human2D:
    #joints positions
    # with 3 points of contact fixed
    hip:NDArray=None # Fixed ->saddle
    foot:NDArray=None # Fixed->pedal
    heel:NDArray=None
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
    elbow_bend:float=None
    elbow:NDArray=None
    ###########################

    torso_len: float =None
    u_leg_len: float =None
    l_leg_len: float =None
    foot_len:float=None
    foot_angle:float=None
    ankle_mobility:float=5. # +- angle range (in degrees) of ankling
    ankle_height:float=50
    cleat_set_back:float=0

    bike: Bike=field(default_factory=Bike)
    # For animation
    lines:dict[str,list[Line2D]]=field(default_factory= dict)

    # update position of fixed points
    def update_hip(self, new_pos:NDArray)->None:
        self.hip=new_pos
    def update_wrist(self, new_pos:NDArray)->None:
        self.wrist=new_pos

    def update_foot(self, new_pos:NDArray, ang_shift:float=0.)->None:
        '''
        new_pos is the position of the pedal spindle
        so one has to include cleat_set back
        '''
        direction=self.bike.side_to_sign()
        
        foot_angle_temp=((self.foot_angle+ang_shift)*np.pi/180) 
        
        self.foot=np.array([
            new_pos[0]+direction*self.cleat_set_back*np.cos(foot_angle_temp),
            new_pos[1]-self.cleat_set_back*np.sin(foot_angle_temp)            
        ])
        
        self.heel=self.foot+ np.array([
            -direction*self.foot_len*np.cos(foot_angle_temp),
            self.foot_len*np.sin(foot_angle_temp)
        ])

        # new ankle approach
        upper_foot=np.sqrt(self.foot_len**2 + self.ankle_height**2)
        foot_angle_temp += np.arctan2(self.ankle_height,self.foot_len)
        
        self.ankle=self.foot+ np.array([
            -direction*upper_foot*np.cos(foot_angle_temp),
            upper_foot*np.sin(foot_angle_temp)
        ])

        #self.ankle=ankle_pos 


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
            raise Exception("Overextension of the leg")
        else:
            #use cosine theorem to deal with knee angles
            cos_alpha = (self.u_leg_len**2 + len_diff**2 - self.l_leg_len**2) / (2 * self.u_leg_len*len_diff )
            
            #true knee angle
            # use clip to avoid floating point errors
            alpha = np.arccos(np.clip(cos_alpha, -1.0, 1.0))
            
            # 3. leg angle with respect to x,y coordinate system
            beta = np.arctan2(diff[1], diff[0])
            
            # 4. pick "physical" knee angle 
            # transfored to x,y coordante system
            sign=self.bike.side_to_sign()
            angle = beta + sign*alpha 

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

        #Arms are bend so we are now dealing with 
        # an effecive arm length wich is sorten 
        #from the full length due to elbow bend
        # 1) using sine theorem get U_ang
        L_ang=self.elbow_bend*np.pi/180
        U_ang=np.arcsin(np.clip(self.l_arm_len*np.sin(L_ang)/self.u_arm_len, -1.,1.))
        # 2) get the elbow angle gamma
        gamma=np.pi-L_ang-U_ang #-> we have a triangle L_ang+U_ang+gamma=180
        # 3) using cosine theorem
        #effective_arm=self.u_arm_len*np.cos(U_ang)+ self.l_arm_len*np.cos(L_ang)
        effective_arm=np.sqrt(
            self.u_arm_len**2 + self.l_arm_len**2\
                -2.*self.u_arm_len*self.l_arm_len*np.cos(gamma)
        )
        
        if len_diff > (effective_arm+self.torso_len):
            self.shoulder= self.hip +(diff/len_diff)*self.torso_len 
            self.elbow=self.hip +(diff/len_diff)*self.torso_len
            raise Exception("Overextension of the back")
        else:
            #use cosine theorem to deal with knee angles
            cos_alpha = (self.torso_len**2 + len_diff**2 - effective_arm**2) / (2 * self.torso_len*len_diff )
            # use clip to avoid floating point errors
            alpha = np.arccos(np.clip(cos_alpha, -1.0, 1.0))
            
            beta = np.arctan2(diff[1], diff[0])
            #pick "physical" shoulder angle --> only plus sign solution
            direction=self.bike.side_to_sign()
            angle = beta +direction*alpha # if self.hip[0] < self.wrist[0] else beta - alpha
            #Update shoulder (WORKS!)
            self.shoulder = np.array([
                self.hip[0] + self.torso_len* np.cos(angle),
                self.hip[1] + self.torso_len* np.sin(angle)
            ])

            #update elbow
            diff2= self.shoulder- self.wrist
            #pick the smaller angle from arctan
            ang_temp= np.arctan2(diff2[1],diff2[0])
            #ang_temp=(ang_temp+np.pi)%(2.*np.pi)-np.pi
            true_ang=ang_temp + direction*(self.elbow_bend)*np.pi/180
            
            #print(f'True ang ={true_ang}')
            self.elbow = np.array([
                self.wrist[0]+self.l_arm_len*np.cos(true_ang),
                self.wrist[1]+self.l_arm_len*np.sin(true_ang)
            ])


    #For animations
    def start_pedaling(self,frame,saddle_loc:NDArray=np.zeros(2))->None:
        '''
        Helper function intoruding dynamics->pedalling
        as a function of frame=time
        '''
        t = frame / 1.0
        crank_len=self.bike.crank_len
        bb_loc=self.bike.calc_bb_loc(saddle_loc)
        direction=self.bike.side_to_sign()
        #Here I should first update the foot angle
        #before I do update of the foot ->ankle
        # and do the update knee at the end
        # The idea is to have ( according to Gemini)
        # 20deg at the top
        # around 5-10 in the push (~3 o'clock)
        # 10-20 at the bottom -> depending on the user input
        # 15-25 around 9 o'clock
        # So we need a trigonometric function of time
        # that will return 
        # to the initial state at the bottom of
        # the pedal stroke
        # Decided to give this additinal angle to 
        # class method update_foot
        
        self.update_foot(
            np.array([
            bb_loc[0] - direction* crank_len * np.cos(t),
            bb_loc[1] + crank_len * np.sin(t)
            ]),
            self.ankle_mobility*np.cos(t)
        )
        
        self.update_knee()      

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
            bb_loc[0] - direction* self.bike.crank_len * np.cos(frame),
            bb_loc[1] + self.bike.crank_len * np.sin(frame)
            #self.foot[0]-direction*self.cleat_set_back*np.cos(self.foot_angle*np.pi/180),
            #self.foot[1]+self.cleat_set_back*np.sin(self.foot_angle*np.pi/180)
        ])
        x.extend([self.foot[0],self.ankle[0],self.knee[0],self.hip[0],self.shoulder[0],self.elbow[0],self.wrist[0]])
        y.extend([self.foot[1],self.ankle[1],self.knee[1],self.hip[1],self.shoulder[1],self.elbow[1],self.wrist[1]])
        
        ## New
        x.extend([None,self.ankle[0],self.heel[0],self.foot[0],None])
        y.extend([None,self.ankle[1],self.heel[1],self.foot[1],None])
        
        x_crank.extend([spindle_loc[0],bb_loc[0]])
        y_crank.extend([spindle_loc[1],bb_loc[1]])

        return x,y,x_crank,y_crank
    

    #import legacy stuff for backwards compatibity
    setup_plot_pyplot=setup_plot_pyplot
    animation_step_pyplot=animation_step_pyplot
    ## END    

# Initialize the plots 
def setup_plot_pyplot(self, ax,col:str='k'):
    '''
    Initialize the plotting objects
    '''
    self.bike.plot_bike(ax,np.zeros(2))
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
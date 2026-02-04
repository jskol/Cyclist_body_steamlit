class AnimationSettings:
    def __init__(self,number_of_frames:int=60,show_angles:bool=False,color_scheme:dict[str,str]={})->None:
        self._number_of_frames=number_of_frames
        self._show_angles=show_angles
        if not color_scheme:
            self._color_scheme={'Human': '#ffda00',  'Joints': "#de58fb"}

    @property
    def number_of_frames(self)->int:
        return self._number_of_frames
    @number_of_frames.setter
    def number_of_frames(self, new_val)->None:
        self._number_of_frames=new_val
    
    @property
    def show_angles(self)->bool:
        return self._show_angles
    @show_angles.setter
    def show_anlges(self,new_val)->None:
        if not isinstance(new_val,bool):
            raise TypeError("Show angle has to be boolian")
        self._show_angles=new_val
    
    @property
    def color_scheme(self)->dict[str,str]:
        return self._color_scheme
    @color_scheme.setter
    def color_scheme(self, new_dict:dict[str,str])->None:
        self._color_scheme=new_dict

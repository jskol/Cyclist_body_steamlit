from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

fig,ax=plt.subplots()


plot_data = ax.plot([],[])
ax.set_xlim(0,10),ax.set_ylim(-1,1)
def update_phase(frame:int)->list[Line2D]:
    phase=frame*0.1
    x =np.linspace(0,10,100)
    plot_data[0].set_data(x,(1+0.1*np.cos(phase))*np.sin(x+phase))
    return plot_data


animation=FuncAnimation(
        fig=fig,
        func=update_phase,
        frames=100,
        interval=10
)

plt.show()
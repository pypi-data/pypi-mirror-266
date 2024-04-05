import spiakid_DRS.SpectralRes.Data as Dt
import numpy as np
from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



def interface(data_file):

    def plot_recons(event):
        time = int(var.get())
        Text['text'] = str(t[time]) + ' s'
        ph_inter = np.zeros(shape = (num,num))
        for i in range(num):
            for j in range(num):
                ph_inter[i,j] = ph[i,j][time]
        fig.clear()
        axes = fig.add_subplot(111)
        surf = axes.imshow(ph_inter,cmap = 'gray_r')
        fig.colorbar(mappable=surf)
        canvas.draw()

    

    data = Dt.read_hdf5(data_file)
    
    time_step = 0.01
    obs_time = data['Config']['1-Photon_Generation']['telescope']['exposition_time']
    num = int(np.sqrt(len(data['Photons'])))
    mini = []
    maxi = []
    for i in range(num):
        for j in range(num):
            pix = data['Photons'][str(i)+'_'+str(j)]
            if len(pix[0]) > 0:
                mini.append(min(pix[1]))
                maxi.append(max(pix[1]))
    maxi = max(maxi)
    mini = min(mini)

    time_bins = int(obs_time/time_step)
    t = np.arange(0,time_bins,time_step)
    ph = np.zeros(shape = (num,num), dtype=object)
    for i in range(num):
        for j in range(num):
            pix = data['Photons'][str(i)+'_'+str(j)]
            H,b = np.histogram(pix[0],bins = time_bins)
            ph[i,j] =H
    ph_inter = np.zeros(shape = (num,num))
    for i in range(num):
        for j in range(num):
            ph_inter[i,j] = ph[i,j][0]
    root = Tk()
    root.grid()
    fig = Figure()
    axes = fig.add_subplot(111)
    surf = axes.imshow(ph_inter,cmap = 'gray_r')
    fig.colorbar(mappable=surf)
    canvas = FigureCanvasTkAgg(fig,master = root) 
    canvas.draw()
    canvas.get_tk_widget().grid(column = 0,row = 0)



    var = DoubleVar()
    scale = Scale(root, variable=var,from_=0,to=time_bins,orient=HORIZONTAL,length=1000,showvalue=0)
    scale.grid(column = 0,row = 1)    
    scale.bind("<ButtonRelease-1>",plot_recons)
    Text = Label(root,text='0 s')
    Text.grid(column = 0, row = 3,columnspan=2)


    root.mainloop()


interface(data_file='/spiakid/data/Simulation_Image/Simulation_phase_10s.hdf5')
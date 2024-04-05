import streamlit as st
import spiakid_DRS.SpectralRes.Data as Dt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure



st.set_page_config(page_title='Recons_interface')

st.title('Reconstruction Interface')


data_location = st.text_input('Data Location',value=None)
value = 0

if data_location != None:
 
         
    data = Dt.read_hdf5(data_location)
    num = int(np.sqrt(len(data['Photons'])))
    time_step = 0.01
    obs_time = data['Config']['1-Photon_Generation']['telescope']['exposition_time']
    time_bins = int(obs_time/time_step)
    t = np.arange(0,time_bins,time_step)
    time =st.slider(label='Hello',min_value=0,max_value=time_bins-1,value=0,label_visibility='collapsed')
    st.write("Time bins:", t[time])
    col1, col2, = st.columns([1, 1])
        
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
    E_range = maxi-mini
    E_bins = np.linspace(mini,maxi,10)
    E_bands = []
    for i in range(len(E_bins)-1):
        E_bands.append((E_bins[i]+E_bins[i+1])/2)
    value = np.zeros(shape=(num,num),dtype = object)
    for i in range(num):
        for j in range(num):
            pix = data['Photons'][str(i)+'_'+str(j)]
            value[i,j],xedge,yedge = np.histogram2d(x = pix[0],y=pix[1],bins = [time_bins,E_bins])
    col1,col2 =st.columns([1, 1])
    with col1:        
        ph = np.zeros(shape = (num,num))
       
        for i in range(num):
            for j in range(num):
                ph[i,j] = sum(value[i,j][time,:])
  

        max_ph = np.max(ph)
        fig1 = Figure(figsize=(8,8))
        ax1 = fig1.add_subplot(111)
        surf = ax1.imshow(ph,cmap = 'gray_r',origin='lower')
        ax1.set_title('Photon number',fontsize=20)
        fig1.colorbar(mappable=surf)
        st.pyplot(fig1)


    with col2:


        fig2 = Figure(figsize=(8,8))
        ax2 = fig2.add_subplot(111)
        x_offset = len(E_bands)+50
        y_offset = max_ph + 2
        plt.setp(ax2,'frame_on',False)
        ax2.set_xticks([])
        ax2.set_yticks([])


        for k in range(num):
            for l in range(num):
                ax2.plot(np.array(E_bands)+ l*x_offset, np.array(value[k,l][time,:] )+ k*y_offset,'r-o',ms=1, mew=0, mfc='r')
        ax2.set_xlabel('Phase from '+str(round(E_bands[0]))+' to '+str(round(E_bands[-1]))+' degrees',fontsize=20)
        ax2.set_ylabel('# Count from 0 to '+str(int(max_ph)),fontsize=20)
        st.pyplot(fig2)


    
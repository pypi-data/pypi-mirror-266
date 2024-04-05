import numpy as np
import scipy.signal as sg
from scipy.optimize import least_squares
import matplotlib.pyplot as plt
import spiakid_DRS.SpectralRes.utility as ut



def Energy_Resolution_pulse(pulseheight, binsize, savefolder):

    r"""Plot histogram of the height of all the pulse and the fit of gaussians representing the photon number

    Parameters
    ----------

    data: Dictionnary
        Contains the height of the pulse (need to be created from the Pixel class)
    
    binsize: int
        The size of the bins

    photonum: int
        How many gaussians you want to fit 
    
    Format: list
        Indicates the image format
    
    savefolder: list
        Indicates in which folder to save the histogram

    Returns
    -------
    figS : ``matplotlib.pyplot.figure``
        A ``matplotlib.pyplot`` figure object.

    """
    
    #Pulse Height Histogram and the fitting gaussians

    pmin = np.min(-pulseheight)
    pmax = np.max(-pulseheight)
    bins = np.arange(pmin,pmax+binsize ,binsize)
    a = np.histogram(-pulseheight,bins)
    y = a[0]
    vals = sg.find_peaks(y,width = 5)
    x = a[1]
    x = x[:-1]
    plt.figure()
    plt.hist(-pulseheight,bins)
    plt.xlabel('Pulse Height(deg)')
    plt.ylabel('Counts')
    center = []
    sigma_list = []
    peaks_indx = vals[0]
    center0 = x[peaks_indx[0]]
    dpeak = x[peaks_indx[1]] - center0
    #computing gaussians
    for i in range(2):

        sigma , mu,amp = ut.fit_gauss(y,x,x[vals[0][0]]+ i * dpeak)
        center.append(mu)
        sigma_list.append(sigma)
        y = y - 1/(np.sqrt(2*np.pi)*sigma)*amp * np.exp(-(x-mu)**2/(2*sigma**2))
        plt.plot()
        plt.plot(x,1/(np.sqrt(2*np.pi)*sigma)*amp * np.exp(-(x-mu)**2/(2*sigma**2)),'--',linewidth = 3,color = 'red',alpha = 0.5)
        
        peak = amp/sigma/np.sqrt(2*np.pi)
    
        plt.text(center[i] + 0.5,peak+2,'n=%d'%(i),fontsize = 18)

        #Computing Resolution
    R = 1/2/np.sqrt(2*np.log(2)) * (center[1]-center[0])/sigma_list[1]

        
    plt.annotate('$\\frac{E}{\Delta E}$' + '= %1.1f @ n=1' %(R), xy=(1,1), xytext=(-130, -12), va='top',
                 xycoords='axes fraction', textcoords='offset points',fontsize = 20)

    plt.savefig(savefolder + 'Energy_Resolution_pulsed.png',bbox_inches = 'tight')
    plt.close()


def Energy_Resolution_cont(pulseheight, binsize, savefolder):

    r"""Plot histogram of the height of all the pulse and the fit of gaussians representing the photon number

    Parameters
    ----------

    data: Dictionnary
        Contains the height of the pulse (need to be created from the Pixel class)
    
    binsize: int
        The size of the bins

    photonum: int
        How many gaussians you want to fit 
    
    Format: list
        Indicates the image format
    
    savefolder: list
        Indicates in which folder to save the histogram

    Returns
    -------
    figS : ``matplotlib.pyplot.figure``
        A ``matplotlib.pyplot`` figure object.

    """
    
    #Pulse Height Histogram and the fitting gaussians

    pmin = np.min(-pulseheight)
    pmax = np.max(-pulseheight)
    bins = np.arange(pmin,pmax+binsize ,binsize)
    a = np.histogram(-pulseheight,bins)
    y = a[0]
    vals = sg.find_peaks(y,width =5)
    x = a[1]
    x = x[:-1]
    plt.figure()
    plt.hist(-pulseheight,bins)
    plt.xlabel('Pulse Height(deg)')
    plt.ylabel('Counts')
    center = []
    sigma_list = []
    peaks_indx = vals[0]



    sigma , mu,amp = ut.fit_gauss(y,x,x[vals[0][0]])
    center.append(mu)
    sigma_list.append(sigma)
    y = y - 1/(np.sqrt(2*np.pi)*sigma)*amp * np.exp(-(x-mu)**2/(2*sigma**2))
    plt.plot()
    plt.plot(x,1/(np.sqrt(2*np.pi)*sigma)*amp * np.exp(-(x-mu)**2/(2*sigma**2)),'--',linewidth = 3,color = 'red',alpha = 0.5)
        
    peak = amp/sigma/np.sqrt(2*np.pi)
    
    plt.text(center[0] + 0.5,peak+2,'n=%d'%(1),fontsize = 18)

        #Computing Resolution
    R = 1/2/np.sqrt(2*np.log(2)) * (center[0])/sigma_list[0]

        
    plt.annotate('$\\frac{E}{\Delta E}$' + '= %1.1f @ n=1' %(R), xy=(1,1), xytext=(-130, -12), va='top',
                 xycoords='axes fraction', textcoords='offset points',fontsize = 20)

    plt.savefig(savefolder + 'Energy_Resolution_cont.png',bbox_inches = 'tight')
    plt.close()



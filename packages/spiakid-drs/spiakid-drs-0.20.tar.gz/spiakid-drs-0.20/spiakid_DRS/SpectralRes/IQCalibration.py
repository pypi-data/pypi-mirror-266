import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import scipy.interpolate as interp;
import spiakid_DRS.SpectralRes.utility as ut


def IQ_binary_old(filename):
    
    data = np.fromfile(filename,dtype=float,count = -1,sep = '')
    data_len = int((len(data)-1)/2)
    
    time = data[0]*np.arange(0,data_len)
    I = data[1:data_len+1]
    Q = data[data_len+1:]
    return time,I, Q

def IQ_binary_new(filename):
    
    data = np.fromfile(filename,dtype=float,count = -1,sep = '')
    data_len = int(data[1])
    
    time = data[0]*np.arange(0,data_len)
    I = data[2:data_len+2]
    Q = data[data_len+2:]
    return time,I, Q

def GetAmpPhaseError(t,I,Q,IF_freq,isplotting = False):
    
    #take the I as an reference for calibration
  
    poptQ,pcovQ = curve_fit(lambda t,A,phi,Q0: ut.fit_sin(t,A,phi,Q0,IF_freq),t,Q)

    poptI,pcovI = curve_fit(lambda t,A,phi,I0: ut.fit_cos(t,A,phi,I0,IF_freq),t,I)

    AQ = poptQ[0]
    phiQ = poptQ[1]
    Q0 = poptQ[2]
    
    # print("AQ:",AQ)
    # print("APhi:",phiQ)

    AI = poptI[0]
    phiI = poptI[1]
    I0 = poptI[2]
    
    delta_amp = AI/AQ
    delta_phi = phiQ-phiI
    
    if isplotting == True:
        I_fit = ut.fit_cos(t,AI,phiI,I0,IF_freq)
        Q_fit = ut.fit_sin(t,AQ,phiQ,Q0,IF_freq)
        
        f,(ax1,ax2) = plt.subplots(2,1,sharex = True)
        ax1.plot(t*1e6,I,label = 'I Meas')
        ax1.plot(t*1e6,I_fit,label = 'I Fit')
        
        ax1.legend()
        
        plt.title("$\Delta A$:{0:.3f} $\Delta \phi$:{1:.3f}".format(delta_amp,delta_phi))
        
        # ax1.text()
        
        ax1.set_ylabel("I(V)",fontsize = 20)
        
        ax2.plot(t*1e6,Q,label = 'Q Meas')
        ax2.plot(t*1e6,Q_fit,label = 'Q Fit')
        
#        ax1.ylabel("Q(V)")
        ax2.set_xlabel("Time($\mu s$)",fontsize = 20)
        ax2.set_ylabel("Q(V)",fontsize = 20)
        ax2.legend()
        plt.tight_layout()
        
        
    
    return delta_amp,delta_phi,I0,Q0
    
def IQCal(I,Q,delta_A,delta_phi,I0 = 0,Q0 = 0):
    
    #calibrate the DC offset
    #I: the raw I data
    #Q: the raw Q data
    #delta_A: the radio of the amp of Q and I
    #delta_phi: the phase imbalance between I and Q
    #I0,Q0: the DC offset of I and Q
    
    I1 = I-I0;
    Q1 = Q-Q0;
    Q1 = Q1*delta_A;
   
    
#    phi = np.arctan2((Q1 - I1*np.cos(delta_phi))/I1/np.cos(delta_phi))
    phi = np.arctan2(Q1 - I1*np.sin(delta_phi),I1*np.cos(delta_phi) )
#    plt.plot(phi)
    
    
    amp = np.sqrt((I1**2 + Q1**2)/(np.cos(phi)**2+np.sin(phi+delta_phi)**2));
    
    I_cal = amp*np.cos(phi)
    Q_cal = amp*np.sin(phi)
    
    return I_cal,Q_cal
    
def IQ_CalS21FromFile(IQ_file,IQ_caldata=None):
    

    indx,freq,I,Q,I0,Q0 = np.loadtxt(IQ_file,unpack = True)
    # indx,freq,I_thru,Q_thru,I0_thru,Q0_thru = np.loadtxt(IQ_thrufile,unpack = True)
    
    
    freq_cal = IQ_caldata[:,0]
    amp_imbalance = IQ_caldata[:,1]
    phase_imbalance = IQ_caldata[:,2]

    f_amp = interp.interp1d(freq_cal,amp_imbalance)
    f_phase = interp.interp1d(freq_cal,phase_imbalance)

    delta_A = f_amp(freq)
    delta_phase = f_phase(freq)    

    I_cal,Q_cal =IQCal(I,Q,delta_A,delta_phase, I0 = I0,Q0 = Q0)
    
    
    return freq,I_cal,Q_cal,I0,Q0

def IQ_CalS21(freq,I,Q,I0,Q0,IQ_caldata=None):
    
    # indx,freq,I,Q,I0,Q0 = np.loadtxt(IQ_file,unpack = True)
    # indx,freq,I_thru,Q_thru,I0_thru,Q0_thru = np.loadtxt(IQ_thrufile,unpack = True)
    
    
    
    
    if IQ_caldata is not None:
        freq_cal = IQ_caldata[:,0]
        amp_imbalance = IQ_caldata[:,1]
        phase_imbalance = IQ_caldata[:,2]
    
        if np.max(freq) > np.max(freq_cal):
            print("IQ cal out of range no calibration is done")
            return I,Q,I0,Q0 
        

        f_amp = interp.interp1d(freq_cal,amp_imbalance)
        f_phase = interp.interp1d(freq_cal,phase_imbalance)

        delta_A = f_amp(freq)
        delta_phase = f_phase(freq)
        
    else:
        
        delta_A = np.ones_like(freq)
        delta_phase = np.zeros_like(freq)
        
        
    I_cal,Q_cal =IQCal(I,Q,delta_A,delta_phase, I0 = I0,Q0 = Q0)
    
    
    return I_cal,Q_cal,I0,Q0

def IQ_CalS21_VNA(IQ_file):
    
    data = np.loadtxt(IQ_file)
    
    freq = data[:,1]
    amp = data[:,2]
    phase = data[:,3]
    
    S21 = 10**(amp/20)*np.exp(1j*phase)
    
    I = np.real(S21)
    Q = np.imag(S21)
    
    return freq,I,Q
    
def IQ_CalNoise(I,Q,freq_noise,freq,I0,Q0,IQ_caldata):
    
    indx,delta_A,delta_phase,I0_noise,Q0_noise = IQ_noiseCaldata(freq_noise,freq,I0,Q0,IQ_caldata)
    
    ICal,QCal = IQCal(I,Q,delta_A,delta_phase,I0_noise,Q0_noise)
    
    return ICal,QCal
    
def IQ_noiseCaldata(freq_noise,freq,I0,Q0,IQ_caldata):
    
    
    freq_cal = IQ_caldata[:,0]
    amp_imbalance = IQ_caldata[:,1]
    phase_imbalance = IQ_caldata[:,2]

    f_amp = interp.interp1d(freq_cal,amp_imbalance)
    f_phase = interp.interp1d(freq_cal,phase_imbalance)

    delta_A = f_amp(freq_noise)
    delta_phase = f_phase(freq_noise)  
    
    indx = np.argmin(np.abs(freq-freq_noise))
    
    I0_noise = I0[indx]
    Q0_noise = Q0[indx]
    
    
    # I_cal,Q_cal =IQCal(I_noise,Q_noise,delta_A,delta_phase, I0 = I0,Q0 = Q0)

    return indx,delta_A,delta_phase,I0_noise,Q0_noise











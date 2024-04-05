import multiprocessing as mp
import numpy as np
import scipy.signal as sg

import spiakid_DRS.SpectralRes.Data as Dt
import spiakid_DRS.SpectralRes.resonator as R
import spiakid_DRS.SpectralRes.cmplxIQ as fitmodel
import spiakid_DRS.SpectralRes.IQCalibration as IQCal
import spiakid_DRS.SpectralRes.utility as ut


def GenPulseAverageWithHDF(res,hdfile,IQCaldata,process_nb,t_offset = 0.001):
        
        #res: scraps.resonator obj
        
        #hdfile: the hdfile contain the pulse data
        
        #savefolder: directory to save the processed the data
        
        #IQCaldata: IQ Calibration data for the raw pulse data
        
        #calibrate_drift: bool, to remove the drift in the baseline or not. 
        
        #t_offset: to move the trigger time of the pulse. t_offset = 0 means the trigger of the pulse is in the center
            
        #savefig: bool, to produce the plot of the averaged data or not
        
        #load the dataset of the pulse in the hdfile
        pulse = hdfile['pulse']
        
        #the frequency of the trigger of the laser.
        pulselaser = pulse['laserfreq']
        
        #the data of the pulse is segmented. Load the number of the groups
        NumpulseUnscaled = pulse['groupnum']
        
        #load the sample frequency of the data. The usual sample rate is about 100MHz
        dt = 1/pulse['samplefreq']

        vgains = pulse['vgains'][...]
        voffsets = pulse['voffsets'][...]

            
        #load the DC offset of the IQ from the res
        I0 = res.I0
        Q0 = res.Q0
        freq = res.freq
            
        #load the readout tone frequency
        pulsefreq = pulse['measfreq']
        
        #calculate the number of data point in one period of the laser pulse
        pulsePointNum = round(1/pulselaser/dt)
        Ip_av = np.zeros(pulsePointNum)
        Qp_av = np.zeros(pulsePointNum)
        pulseIRawslist = []
        pulseQRawslist = []
        pool = mp.Pool(process_nb)
        res_par = []
        resfreqindx = np.argmin(np.abs(freq-pulsefreq))

        Ip_initial = res.I[resfreqindx]
        Qp_initial = res.Q[resfreqindx]
        for i in range(NumpulseUnscaled):  
            results = pool.apply_async(avedata_par,args=(pulse['IQ%d'%(i)][...],vgains,voffsets,pulsefreq,freq,I0,Q0,IQCaldata,res,i,dt,pulselaser,t_offset,Ip_initial,Qp_initial))
            res_par.append((i,results))

        for i, result in res_par:

            _,value = result.get()
            Ip_av = value[0] + Ip_av
            Qp_av = value[1] + Qp_av
            pulseIRawslist.append(value[2])
            pulseQRawslist.append(value[3])
            

            
        pool.close()
        pool.join()

        t_seg = np.arange(0,len(Ip_av))*dt
            
        # res.pulseUnscaled = []

        #generate the IQ of the pulse
        Ip_av = Ip_av/NumpulseUnscaled
        Qp_av = Qp_av/NumpulseUnscaled
        
        #calculate the amplitude and phase response of the MKIDs
        amp,phase = res.cal_pulse_outside(Ip_av + 1j*Qp_av,pulsefreq,pulsewidth = 50)

        data = {"pulsefreq":pulsefreq,
                'res':res,
                't':t_seg,
                'Ia':Ip_av,
                'Qa':Qp_av,
                'amp':amp,
                'phase':phase,
                't_offset':t_offset,
                'dt':dt}
            
        return data,pulseIRawslist,pulseQRawslist

def avedata_par(pulsedata,vgains,voffsets,pulsefreq,freq,I0,Q0,IQCaldata,res,i,dt,pulselaser,t_offset,Ip_initial,Qp_initial):

 
            #scale the data from the oscillscope
        I = pulsedata[0]*vgains[0] - voffsets[0]
        Q = pulsedata[1]*vgains[1] - voffsets[1]
            
            #calibrate the IQ imbalance from the IQ mixer, i.e. the DC offset, amplitude and phase imbalance
        I,Q = IQCal.IQ_CalNoise(I,Q,pulsefreq/1e9,freq/1e9,I0,Q0,IQCaldata)

            #segment the data by laser frequency
        Ip,Qp,pulseIRaws,pulseQRaws = ut.GenAveragePulse(I,Q,dt = dt,pulsefreq = pulselaser,t_offset = t_offset)

        #to remove the DC offset or not
        points = int((1/pulselaser/2 - t_offset)/dt)
       
        Ip = Ip - np.mean(Ip[0:points]) + Ip_initial 
        Qp = Qp - np.mean(Qp[0:points]) + Qp_initial 
            
            #calculate the average of the pulse

        return(i,[Ip,Qp,pulseIRaws,pulseQRaws] )

def GenPulseStatisticsHDF(res, hdfile, wienerfilter,pulseIRaws,pulseQRaws,t_seg ,binsize, t_offset,pulsetype,nb_process):
        

    # load the dataset of the pulse in the hdfile
    pulse = hdfile['pulse']
    # the frequency of the trigger of the laser.
    pulselaser = pulse['laserfreq']

        # the data of the pulse is segmented. Load the number of the groups
    NumpulseUnscaled = pulse['groupnum']

        # load the sample frequency of the data. The usual sample rate is about 100MHz
    dt = 1/pulse['samplefreq']
    measfreq = pulse['measfreq']
    resfreqindx = np.argmin(np.abs(res.freq-measfreq))
    Ip_initial = res.I[resfreqindx]
    Qp_initial = res.Q[resfreqindx]
    pulse_height = []
    phase_pulse = []
    res_par = []
    pool = mp.Pool(nb_process)
    for i in range(NumpulseUnscaled):#NumpulseUnscaled
        results = pool.apply_async(par_stat,args=(pulseIRaws[i],pulseQRaws[i],pulselaser,t_offset,dt,Ip_initial,Qp_initial,t_seg,binsize,measfreq,pulsetype,wienerfilter,res,i))
        res_par.append((i,results))
    for i, result in res_par:

        _,value = result.get()
        pulse_height.append(value[0])
        phase_pulse.append(value[1])
    pool.close()
    pool.join()
    pulseheight = sum(pulse_height,[])
    return(np.array(pulseheight),phase_pulse)

def par_stat(pulseIRaws,pulseQRaws,pulselaser,t_offset,dt,Ip_initial,Qp_initial,t_seg,binsize,measfreq,pulsetype,wienerfilter,res,i):
    pulse_height = []

    for pulseIndx in range(len(pulseIRaws)):

        Iv = pulseIRaws[pulseIndx]
        Qv = pulseQRaws[pulseIndx]

        points = int((1/pulselaser/2 - t_offset)/dt)

     
        Iv = Iv - np.mean(Iv[0:points]) + Ip_initial
        Qv = Qv - np.mean(Qv[0:points]) + Qp_initial


        t_bin, Iv_bined = ut.AverageArray(t_seg, Iv, chuncksize=binsize)
        t_bin, Qv_bined = ut.AverageArray(t_seg, Qv, chuncksize=binsize)

        pulse_amp, pulse_phase = res.cal_pulse_outside(Iv_bined + 1j*Qv_bined, measfreq)

        avenum = int((1/pulselaser/2 - t_offset)/binsize/dt)
        if pulsetype == 'phase':

            pulse_phase = np.unwrap(pulse_phase)

            phase0 = np.mean(pulse_phase[0:avenum])

            pulse_degree = (pulse_phase-phase0)

            pulse_degree = np.unwrap(pulse_degree)*180/np.pi
            pulse_wiener = sg.lfilter(wienerfilter, 1, pulse_degree)

            indxpulse = len(wienerfilter)

            p_min = np.min(pulse_wiener[indxpulse-5:indxpulse+5])

            pulse_height.append(p_min)

        else:

            amp0 = np.mean(pulse_amp[0:avenum])

            pulse_amp = (pulse_amp-amp0)

            pulse_amp = pulse_amp*180/np.pi
            pulse_wiener = sg.lfilter(wienerfilter, 1, pulse_amp)

            indxpulse = len(wienerfilter)

            p_min = np.min(pulse_wiener[indxpulse-5:indxpulse+5])

            pulse_height.append(p_min)
    
    
    return(i,[pulse_height,pulse_degree])

def ContSpectralRes(res,hdffile,wienerfilter,IQCaldata,binsize,deadtime,threshold,dt,nb_process):


        I0 = res.I0
        Q0 = res.Q0
        freq = res.freq
        vgains = hdffile['vgains']
        voffsets = hdffile['voffsets']

        # load the readout tone frequency
        pulsefreq = hdffile['measfreq']
        NumpulseUnscaled = hdffile['groupnum']
        wiener_pulse_list = []
        wiener_list = []
        pulse_list = []
        arg_pulse = []
        raw_data = []
        if pulsefreq < 1e3:
            pulsefreq = pulsefreq*1e9

        pool = mp.Pool(nb_process)
        res_par = []
        for i in range(NumpulseUnscaled):
      
            results = pool.apply_async(par_cont_stat,args = (hdffile['IQ%d'%(i)],vgains,voffsets,pulsefreq,freq,I0,Q0,IQCaldata,res,binsize,dt,wienerfilter,deadtime,threshold,i))
            res_par.append((i,results))

        for i, result in res_par:

            _,value = result.get()
            wiener_list.append(value[0])
            wiener_pulse_list.append(value[1])
            pulse_list.append(value[2])
            arg_pulse.append(value[3])
            raw_data.append(value[4])
          
        pool.close()
        pool.join()

        wiener_list = sum(wiener_list,[])
        wiener_pulse_list = sum(wiener_pulse_list,[])
        pulse_list = sum(pulse_list,[])

            
        return(wiener_list,wiener_pulse_list,-np.array(pulse_list),arg_pulse,raw_data)

def par_cont_stat(pulsedata,vgains,voffsets,pulsefreq,freq,I0,Q0,IQCaldata,res,binsize,dt,wienerfilter,deadtime,threshold,i):
    
    wiener_pulse_list, wiener_list, pulse_list, arg_pulse = [], [], [], []

    I = pulsedata[0]*vgains[0] - voffsets[0]
    Q = pulsedata[1]*vgains[1] - voffsets[1]

                # calibrate the IQ imbalance from the IQ mixer, i.e. the DC offset, amplitude and phase imbalance
    I, Q = IQCal.IQ_CalNoise(I, Q, pulsefreq/1e9, freq/1e9, I0, Q0, IQCaldata)
                

            
    resfreqindx = np.argmin(np.abs(res.freq-pulsefreq))


    Ip_initial = res.I[resfreqindx]
    Qp_initial = res.Q[resfreqindx]
            

    t = np.arange(0, len(I))*dt
    t_bin, Iv_bined = ut.AverageArray(t, I, chuncksize=binsize)
    t_bin, Qv_bined = ut.AverageArray(t, Q, chuncksize=binsize)
            

    dt_bin = t_bin[1] - t_bin[0]
            
    pulse_amp, pulse_phase= res.cal_pulse_outside(Iv_bined + 1j*Qv_bined, pulsefreq)
            
    pulse_amp0, pulse_phase0 = res.cal_pulse_outside(Ip_initial + 1j*Qp_initial, pulsefreq)
                
    pulse_phase = pulse_phase - pulse_phase0


    pulse_phase = np.unwrap(pulse_phase)*180/np.pi
    pulse_wiener = sg.lfilter(wienerfilter, 1, pulse_phase)
    deadbinnum = round(deadtime/dt_bin) 

    wiener_pulse_list.append(np.where(-pulse_wiener > threshold,-pulse_wiener,0))
    wiener_list.append(-pulse_wiener)
    sig = wiener_pulse_list[-1]
    peaks,_ = sg.find_peaks(sig)
    pulse_list.append(max(sig[0:peaks[0]+5]))
    arg_pulse.append(peaks[0])
    for j in range (1,len(peaks)):
        if peaks[j]- arg_pulse[-1]<deadbinnum:
            pass
        else:
            if j != len(peaks):
                pulse_list.append(max(sig[peaks[j]-5:peaks[j]+5]))
            else:
                pulse_list.append(max(sig[peaks[j]-5:]))
            arg_pulse.append(peaks[j])

    return(i,[wiener_list,wiener_pulse_list,pulse_list,arg_pulse,pulse_phase])
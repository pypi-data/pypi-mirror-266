import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sg
import pickle

import spiakid_DRS.SpectralRes.Data as Dt
import spiakid_DRS.SpectralRes.resonator as R
import spiakid_DRS.SpectralRes.cmplxIQ as fitmodel
import spiakid_DRS.SpectralRes.IQCalibration as IQCal
import spiakid_DRS.SpectralRes.utility as ut
import spiakid_DRS.SpectralRes.fun as fun
import spiakid_DRS.SpectralRes.Plot as sv

class Detect_analysis():
    

    def __init__(self,file,process_nb,output, plot_list,save_list,download_filter = False,deadtime = 50e-6,t_offset = 0.001, binsize_pulse = 100, binsize_hist=0.1):

        print('Reading data')
        self.data = Dt.read_hdf5(file)
        head = self.data['header']
        temp = head['temp']
        pwr = head['power']
        
        
        print('Resonator analysis')
        res_data = self.data['resonator']
        
        freq = res_data['freq']
        I = res_data['I']
        Q = res_data['Q']
        I0 = res_data['I0']
        Q0 = res_data['Q0']
        
        self.res = R.Resonator('1', temp, pwr, freq, I, Q,I0 = I0,Q0 = Q0)
        self.res.load_params(fitmodel.cmplxIQ_params)
        self.res.do_lmfit(fitmodel.cmplxIQ_fit)

        print('Pulse average')
        IQCaldata = self.data['calibration']['IQCaldata']
        #generate the averaged pulse data as the template
        avedata,pulseIRaws,pulseQRaws = fun.GenPulseAverageWithHDF(self.res,self.data,IQCaldata,process_nb, t_offset = t_offset)
        
        if download_filter == False:
            laserfreq = self.data['pulse']['laserfreq']
            print('PSD computing')
            psd = self.GenPSDWithHDF(self.res,self.data,IQCaldata,plot_list,output,binsize = binsize_pulse,pulselaser = laserfreq)
            #generate the psd of the resonator. 

            pulsetriggertime = 1/laserfreq/2 - t_offset
            templatetime = 0.004
            samplefreq = self.data['pulse']['samplefreq']
            #generate the wiener filter for both amplitude and phase
            print('Filter creation')
            self.wifilterphase, wifilteramp,self.indx = self.GenWienerFilter(avedata,psd,plot_list,save_list,output,binsize = binsize_pulse,pulsetriggertime = pulsetriggertime,dt = 1/samplefreq, templatetime = templatetime)
        else:
            file = open(download_filter,'rb')
            self.wifilterphase, wifilteramp,self.indx = pickle.load(file)
            file.close()
        #use the wiener filter to generate the pulse statistics
        print('Pulse stat')
        self.pulseheights,self.pulse_phase = fun.GenPulseStatisticsHDF(self.res,self.data,self.wifilterphase,pulseIRaws,pulseQRaws,avedata['t'], binsize_pulse, t_offset,'phase',process_nb)

        self.resolution, self.centers, self.sigma, self.amp = self.SpectralRes(self.pulseheights,binsize_hist,'pulsed',plot_list,output)
        if 'pulse_hist' in plot_list:
            sv.Energy_Resolution_pulse(self.pulseheights,binsize_hist,output)
        if 'pulseheight_pulse' in save_list:
            file_name = output + 'pulseheight_pulsed.csv'
            file1 = open(file_name,'wb')
            pickle.dump(self.pulseheights,file1)
            file1.close()

        try: self.data['contious']
        except: 
            if 'cont_hist' in plot_list: print('Continuous plot asked, but no continuous data')
        else:
            max_noise = []
            for i in range(len(self.pulse_phase)): max_noise.append(max(self.pulse_phase[i][1000:]))
            self.threshold_noise = np.mean(max_noise)
            self.threshold_sig = self.centers[1] - 3*self.sigma[1]
            if self.threshold_noise >= self.threshold_sig:
                self.threshold = self.threshold_noise
            else:
                self.threshold = self.threshold_sig
            
            print('Continuous pulse stat')
            self.sig,self.filtered_sig,self.cont_pulseheight,self.arg_pulse,self.raw_data = fun.ContSpectralRes(self.res,self.data['contious'],self.wifilterphase,IQCaldata,binsize_pulse,deadtime,self.threshold,1e-8,process_nb)

            self.cont_resolution, self.cont_centers, self.cont_sigma,self.cont_amp = self.SpectralRes(self.cont_pulseheight,binsize_hist,'continue',plot_list, output)
            if 'pulseheight_cont' in save_list:
                file_name = output + 'pulseheight_cont.csv'
                file = open(file_name,'wb')
                pickle.dump(self.cont_pulseheight,file)
                file.close()


    def GenPSDWithHDF(self,res,hdfile,IQCaldata,list_plot,savefolder,binsize = 100,
           pulselaser = 250, NoiseSeglength = None):
    
        
        In,Qn= ut.CalNoiseHDf(res,hdfile['noise'],IQCaldata)
        
        fsample = hdfile['noise']['samplefreq']
        noisefreq = hdfile['noise']['measfreq']
        
        pulsePointNum = round(1/pulselaser*fsample)
        
        
        if  NoiseSeglength == None:
            NoiseSeglength = int(pulsePointNum/binsize)

        # In = np.concatenate(noiseIs)
        # Qn = np.concatenate(noiseQs)
        
        t_seg = np.arange(0,len(In))*1/fsample
        
        t_bin,In_bined = ut.AverageArray(t_seg,In,chuncksize = binsize)
        t_bin,Qn_bined = ut.AverageArray(t_seg,Qn,chuncksize = binsize)
        
        #calculate the amplitude and phase of the noise spectrum
        pulse_amp,pulse_phase = res.cal_pulse_outside(In_bined + 1j*Qn_bined,noisefreq,pulsewidth = 50,fs = 1/(t_bin[1]-t_bin[0]))
        #remove the 2*pi change
        pulse_phase = np.unwrap(pulse_phase)
        
        #calculate the noise spectrum with welth method in the amplitude and phase direction. 
        fpsd,pxx = sg.welch(pulse_phase-np.mean(pulse_phase),fs = 1/(t_bin[1]-t_bin[0]),nperseg = NoiseSeglength)
        fpsd,pyy = sg.welch(pulse_amp-np.mean(pulse_amp),fs = 1/(t_bin[1]-t_bin[0]),nperseg = NoiseSeglength)
        if 'psd' in list_plot:
            plt.figure()
            plt.plot(fpsd,pxx,label = 'Phase noise')
            plt.plot(fpsd,pyy,label='Amp noise')
            plt.legend()
            plt.loglog()
            plt.xlabel('Freq (Hz)')
            plt.ylabel('PSD (rad²/Hz)')
            plt.title('Noise PSD')
            plt.savefig(savefolder+'PSD.png',bbox_inches = 'tight')
            plt.close()
        data = np.vstack([fpsd,pxx,pyy])
        

        return data.T

    def GenWienerFilter(self,templatedata,psd,list_plot,save_list,savefolder,binsize = 500,pulsetriggertime = 0.001,
                    dt = 1e-8, templatetime = 0.003,
                    templatetype = 'average', pulsedirection = 'negtive'):
    
        # data = np.loadtxt("data 3.8885GHz/20220629133637-3.888GHz/Res Index 0/template_average_500.txt")

        # psd = np.loadtxt('20220709164518-4.9 sccm - batch 2/Res Index 1/Temp 50.0mK/noise psd bin 500.txt')
        if templatetype == 'average':

            PI = templatedata['Ia']
            PQ = templatedata['Qa']
            t_seg = templatedata['t']
            
        else: #the template type is single photon pulse

            pass
        

        t_bin,Iv_bined = ut.AverageArray(t_seg,PI,chuncksize = binsize)
        t_bin,Qv_bined = ut.AverageArray(t_seg,PQ,chuncksize = binsize)

        res = templatedata['res']

        # f.close()
        pulsefreq = (res.lmfit_vals[1] + res.lmfit_vals[0])
        amp,phase = res.cal_pulse_outside(Iv_bined + 1j*Qv_bined,pulsefreq)

        trigerindx = int(pulsetriggertime/dt/binsize)
        
        # print(trigerindx)

        phase0 = np.mean(phase[0:trigerindx])
        phase1 = phase - phase0
        phase1 = np.unwrap(phase1)
        
        amp0 = np.mean(amp[0:trigerindx])
        amp1 = amp - amp0

            
        if pulsedirection == 'positive':
            templatephase = phase1/np.max(phase1)
            
        else:
            templatephase = -phase1/np.min(phase1)
            templateamp = -amp1/np.min(amp1)
        
        templatelength = int(templatetime/dt/binsize)
        
        psdlength = (len(psd)-1)*2
        
        wifilterphase = ut.wiener(templatephase[0:templatelength],psd[:,1],psdlength)
        wifilteramp = ut.wiener(templatephase[0:templatelength],psd[:,2],psdlength)
        # wifilter = wiener(templatephase,psd[:,1],800)

        filtered_templatephase = sg.lfilter(wifilterphase,1,templatephase)
        filtered_templateamp = sg.lfilter(wifilteramp,1,templateamp)
        
        indx = np.min(filtered_templatephase)
        if 'filter' in list_plot:
            plt.figure()
            plt.subplot(2,1,1)
            plt.plot(wifilterphase,label = 'Phase filter')
            plt.plot(filtered_templatephase, label = 'Template phase filtered')
            plt.legend()
            plt.xlabel('index')
            plt.ylabel('Pulse height')

            plt.subplot(2,1,2)
            plt.plot(wifilteramp,label = 'Amp filter')
            plt.plot(filtered_templateamp, label = 'Template amp filtered')
            plt.legend()
            plt.xlabel('index')
            plt.ylabel('Pulse height')
            plt.savefig(savefolder+'filter.png',bbox_inches = 'tight')
            plt.close()
        if 'filter' in save_list:
            file_name = savefolder+'filter_data.csv'
            file = open(file_name,'wb')
            pickle.dump([wifilterphase, wifilteramp,indx], file)
            file.close
        return wifilterphase, wifilteramp,indx
    
    
    
    
    def SpectralRes(self,pulseheights,binsize,laser,list_plot,savefolder):
        pmin = np.min(-pulseheights)
        pmax = np.max(-pulseheights)

        bins = np.arange(pmin,pmax+binsize ,binsize)
        a = np.histogram(-pulseheights,bins)
        y = a[0]
        vals = sg.find_peaks(y,width = 5)
        x = a[1]
        x = x[:-1]
        plt.figure()
        plt.hist(-pulseheights,bins)
        plt.xlabel('Pulse Height(deg)')
        plt.ylabel('Counts')
        center = []
        amp_list = []
        sigma_list = []
        
    
        if laser == 'pulsed':
            
                #computing gaussians
            for i in range(2):
                    peaks_indx = vals[0]
                    center0 = x[peaks_indx[0]]
                    dpeak = x[peaks_indx[1]] - center0
                    sigma , mu,amp = ut.fit_gauss(y,x,x[vals[0][0]]+ i * dpeak)
                    center.append(mu)
                    amp_list.append(amp)
                    sigma_list.append(sigma)
                    y = y - 1/(np.sqrt(2*np.pi)*sigma)*amp * np.exp(-(x-mu)**2/(2*sigma**2))
                    plt.plot()
                    plt.plot(x,1/(np.sqrt(2*np.pi)*sigma)*amp * np.exp(-(x-mu)**2/(2*sigma**2)),'--',linewidth = 3,color = 'red',alpha = 0.5)
        
                    peak = amp/sigma/np.sqrt(2*np.pi)
                    plt.text(center[i] + 0.5,peak+2,'n=%d'%(i),fontsize = 18)
            R = 1/2/np.sqrt(2*np.log(2)) * (center[1]-center[0])/sigma_list[1]
            plt.annotate('$\\frac{E}{\Delta E}$' + '= %1.1f @ n=1' %(R), xy=(1,1), xytext=(-130, -12), va='top',
                 xycoords='axes fraction', textcoords='offset points',fontsize = 20)
            if 'pulse_hist' in list_plot:
                plt.savefig(savefolder + 'Energy_Resolution_pulsed.png',bbox_inches = 'tight')
            plt.close()
        elif laser == 'continue':


            sigma , mu,amp = ut.fit_gauss(y,x,x[vals[0][0]])
            center.append(mu)
            amp_list.append(amp)
            sigma_list.append(sigma)
            plt.plot()
            plt.plot(x,1/(np.sqrt(2*np.pi)*sigma)*amp * np.exp(-(x-mu)**2/(2*sigma**2)),'--',linewidth = 3,color = 'red',alpha = 0.5)
            plt.text(center[0] + 0.5,amp/sigma/np.sqrt(2*np.pi)+2,'n=%d'%(1),fontsize = 18)

            R = 1/2/np.sqrt(2*np.log(2)) *  (center[0])/sigma_list[0]
            plt.annotate('$\\frac{E}{\Delta E}$' + '= %1.1f @ n=1' %(R), xy=(1,1), xytext=(-130, -12), va='top',
                 xycoords='axes fraction', textcoords='offset points',fontsize = 20)
            
            if 'cont_hist' in list_plot:
                plt.savefig(savefolder + 'Energy_Resolution_cont.png',bbox_inches = 'tight')
            plt.close()
        return(R,center,sigma_list,amp_list)
    
    



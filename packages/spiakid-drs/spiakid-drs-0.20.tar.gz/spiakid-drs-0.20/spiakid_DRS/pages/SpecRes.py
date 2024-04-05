import streamlit as st
import spiakid_DRS.SpectralRes.Detect as D

st.set_page_config(page_title='SpecRes')
#Interface Creation using streamlit librairy (to ensure a graphical interface in Docker)

st.title('Spectral Resolution')

#Initialisation

plot_list = []
save_list = []
deadtime = 50e-6
t_offset = 0.001
binsize_pulse = 100
binsize_hist=0.1
download_filter = False
#Organisation
col1, col2, col3= st.columns([1, 1, 1])

with col3:
    result_folder = st.text_input('Result folder',value="")

# with col2:
#     txt = st.text('')
#     txt = st.text('')
#     txt = st.text('')
#     format = st.selectbox('Format', ['.jpg','.svg','.eps'])
with col1:
    
    data_location = st.text_input('Data Location',value="")
    process_number = int(st.number_input('Process number',value = 1))


    

    detail = st.checkbox('Details Parameters')
    col1_1, col1_2 = st.columns([0.15, 1])
    if detail:
            with col1_2:
                deadtime = st.number_input('detector deadtime (in s)',value=0.00005, step = 0.000001,format="%.6f")
                t_offset = st.number_input('t_offset',value = 0.001,step = 0.0001,format="%.5f")
                binsize_pulse = st.number_input('average point number', value =100,step = 1)
                binsize_hist = st.number_input('histogram step', value = 0.1,step = 0.1)
                download_filter = st.text_input('Filter path',value = '')
                if download_filter =='': download_filter = False



    output = st.checkbox('Output')
    col2_1, col2_2 = st.columns([0.15, 1])
    if output:
        with col2_2:
            plot = st.checkbox('Saving Plot')
            if plot:
                PSD = st.checkbox('Template')
                filter_plot = st.checkbox('Filter Plot')
                hist_pulse = st.checkbox('Pulsed laser histogram')
                hist_continue = st.checkbox('Continue laser histogram')
                if PSD: plot_list.append('psd')
                if filter_plot: plot_list.append('filter')
                if hist_pulse: plot_list.append('pulse_hist')
                if hist_continue: plot_list.append('cont_hist')

            saving  =st.checkbox('Saving objects')
            if saving:
                filter = st.checkbox('Filter Data')
                pulseheight_pulse = st.checkbox('Pulsed laser pulseheight')
                pulseheight_cont = st.checkbox('Cont laser pulseheight')
                if filter: save_list.append('filter')
                if pulseheight_pulse: save_list.append('pulseheight_pulse')
                if pulseheight_cont: save_list.append('pulseheight_cont')



    Launch = st.button('OK')
    if Launch:
        test = D.Detect_analysis(data_location,process_number,str(result_folder),plot_list,save_list,download_filter, deadtime,t_offset , binsize_pulse , binsize_hist)
    



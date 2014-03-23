 #### importing the necessary libraries
from neurapy.neuroexplorer import nexio
from numpy import *
import scipy
import scipy.signal
    
def get_spiking_data(filename, continuous=None):
    '''filename needs to be a path going to the file; continuous needs to have a value if you want the EMG data'''
    
    ''' this function will have two outputs. Format of first output (neural responses): a[neural id][taste id][trial number].
    Format of second output (EMG responses): b[taste id][trial number]. EMG responses are downsampled to 1 kHz'''
   
    #####################
    ### some default values 
    pre=1499 ### amount of time preceding taste delivery
    post=2501 ### amount of time following taste delivery
    
    ###  Getting spiking, LFP, and event data from .nex file
    data=nexio.read_nex(filename)
    
    data_continuous=nexio.read_nex(filename,load=['continuous'])

    ##############################
    ### getting the taste delivery times
    ##############################
    
    taste_events=[0]*4  ### one for each of the four tastes
    for x in xrange(len(data['Events'])):
        if len(data['Events'][x]['timestamps'])<=1:
            pass
        else:
            taste_id=data['Events'][x]['name'][-2:]
            if taste_id=='03':  ## dilute sucrose
                taste_events[0]=(data['Events'][x]['timestamps']*1000).round()
            elif taste_id=='04': ## strong sucrose
                taste_events[1]=(data['Events'][x]['timestamps']*1000).round()
            elif taste_id=='05': ## dilute quinine
                taste_events[2]=(data['Events'][x]['timestamps']*1000).round()
            elif taste_id=='06': ## dilute quinine
                taste_events[3]=(data['Events'][x]['timestamps']*1000).round()
            else:
                pass
    
    ##############################
    ### getting spiking data
    #############################
    spike_train_all=[]
    
    for neurons in xrange(len(data['Neurons'])):
        spike_train_tastes=[zeros((shape(taste_events[0])[0],pre+post)) for i in range(4)] ### setting up the four-taste spike array for each neuron
        
        neuron_index=data['Neurons'][neurons]
        
        recording_length=int(data['Header']['t end']*1000) ### converting to milliseconds
        spike_train=array([0]*recording_length)  ### setting up the spike train for each neuron
        
        time_stamps=[int(x) for x in (neuron_index['timestamps']*1000).round()]
        
        for x in xrange(len(time_stamps)):  ### putting the 1 into the list of zeros to generate the spike train
            spike_train[time_stamps[x]]=1
        
        for tastes in xrange(len(taste_events)): ### getting the spike train matrix for each of the tastes
            for index,deliveries in enumerate(taste_events[tastes]):
                spike_train_tastes[tastes][index]=spike_train[int(deliveries)-pre:int(deliveries)+post]
        
        spike_train_all.append(spike_train_tastes)  ### collating data across neurons
    

    ##############################
    ### getting EMG data
    #############################
    
    #### function for downsampling EMG signal
    
    def downsample(input_vector,original_frequency,new_frequency):
        if original_frequency==new_frequency:
            return input_vector
        else:
            f=scipy.interpolate.interp1d(arange(0,len(input_vector)),input_vector)
            downsampled_result=f(linspace(0,len(input_vector)-1,len(input_vector)*new_frequency/original_frequency))
            return downsampled_result
    
    ##### actually processing the data 
    
    if continuous is not None:
        for channels in xrange(len(data_continuous['Continuous'])):
            if data_continuous['Continuous'][channels]['name']=='AD18':
                temp_emg_response=data_continuous['Continuous'][channels]['waveform'][0] #### raw EMG response   
                Fq=int(data_continuous['Continuous'][channels]['sampling freq'])  ### frequency at which EMG signal was sampled (Plexon)
                
                bandpass_filter=scipy.signal.butter(3, [300.0/(Fq/2),500.0/(Fq/2)],btype='band')  ### filtered EMG response: 300 to 500 Hz
                filtered_emg_response=scipy.signal.lfilter(bandpass_filter[0],bandpass_filter[1],temp_emg_response)
                
                downsampled_emg_response=downsample(filtered_emg_response,Fq,1000) ### resampling to 1kHz
                
                emg_all=[zeros((shape(taste_events[0])[0],pre+post)) for i in range(4)] ### setting up the multi-taste spike array for each neuron                               
 
                for tastes in xrange(len(taste_events)): ### getting the emg response matrix for each of the tastes
                    for index,deliveries in enumerate(taste_events[tastes]):
                        emg_all[tastes][index]=downsampled_emg_response[int(deliveries-pre):int(deliveries+post)]
    else:
        emg_all='NaN'    
             

    return spike_train_all, emg_all
    





import io_control
import sd_control
import math
import extended_ticks_us
import display


### Global variables ###
global_energy = int(0)
global_filename = ""
global_loop_iteration = 0
global_buffer_size = 8000 # Ustawienie rozmiaru bufora
global_buffer = [global_buffer_size]
global_buffer.clear()
global_is_in_progress = 0
global_last_voltage = float(0)
global_last_current = float(0)


def read_ADS1265():
    global global_last_voltage, global_last_current
    global_last_voltage, global_last_current = io_control.ads1256.get_reading_ADS1256()
    

def descending_log_list(min_val, max_val, num_values):
    if min_val <= 0 or max_val <= 0:
        raise ValueError("min_val and max_val must be greater than 0 for logarithmic scale.")
    if min_val >= max_val:
        raise ValueError("min_val must be less than max_val.")
    if num_values < 2:
        raise ValueError("num_values must be at least 2.")

    # Calculate logarithms
    log_min = math.log10(min_val)
    log_max = math.log10(max_val)

    # Step size in log space
    step = (log_max - log_min) / (num_values - 1)

    # Generate values from max to min (descending)
    values = [10 ** (log_max - i * step) for i in range(num_values)]
    
    est_time = 0
    for x in values:
        est_time = est_time + 5/x
    return values, est_time



def discharge(current, time_us, log_downsample):
    print(f"DC Constant discharge started {current}mA, {time_us/1_000_000:.3f}s")
    global global_energy, global_filename, global_buffer_size, global_buffer, global_last_voltage, global_last_current
    io_control.set_current(current)
    start_time = extended_ticks_us.global_time_tracker.ticks_us()
    end_time = start_time + time_us 
    previous_time = extended_ticks_us.global_time_tracker.ticks_us()
    downsample_tracker = 0

    while extended_ticks_us.global_time_tracker.ticks_us() < end_time:
        read_ADS1265()
        current_time = extended_ticks_us.global_time_tracker.ticks_us()
    
        global_energy += int(global_last_current*(current_time - previous_time)/3.6) #mA * us / 3.6 -> pAh
        previous_time = current_time
        #elapsed_time = time.ticks_diff(time.ticks_us(), start_time)
        if downsample_tracker >= log_downsample:
            global_buffer.append(f"{current_time/1_000:.3f}, {current:.2f}, {global_last_current:.3f}, {global_last_voltage:.2f}, 0, {global_energy/1_000_000:.3f} \n")
            downsample_tracker = 0
        downsample_tracker = downsample_tracker + 1
        
        if len(global_buffer) >= global_buffer_size:
            sd_control.log_to_sd(global_filename)
    
    if global_buffer:
        sd_control.log_to_sd(global_filename)


def eis(current, min_freq, max_freq):
    freq_list, est_time = descending_log_list(min_freq, max_freq, 100)
    print(f"DC EIS started {current}mA, {est_time}s")
    global global_energy, global_filename, global_buffer_size, global_buffer, global_last_voltage, global_last_current
    

    T = 1.2 
    c = max_freq/T

    previous_time = extended_ticks_us.global_time_tracker.ticks_us()


    for x_freq in freq_list:
        io_control.set_current(0)
        print(f"DC Starting with f: {x_freq}")
        inner_start_time = extended_ticks_us.global_time_tracker.ticks_us()
        inner_end_time = inner_start_time + min((5_000_000 / x_freq), 16_000_000)
        sine_const = 2 * math.pi * x_freq / 1_000_000

        previous_voltage = 0
        resample_counter = 0

        while extended_ticks_us.global_time_tracker.ticks_us() < inner_end_time:
            current_inner_time = extended_ticks_us.global_time_tracker.ticks_us() - inner_start_time
            sin_current = current * 0.5 * (1 + math.sin(sine_const * current_inner_time))
            io_control.set_current(sin_current)
            read_ADS1265()

            while previous_voltage != 0 and abs(previous_voltage - global_last_voltage) > 4 and resample_counter < 20:
                print(f"ADS V diff {previous_voltage - global_last_voltage:.2f}mV!")
                read_ADS1265()   
                resample_counter = resample_counter + 1
            resample_counter = 0   
            previous_voltage = global_last_voltage

            current_time = extended_ticks_us.global_time_tracker.ticks_us()
            global_energy += int(global_last_current*(current_time - previous_time)/3.6) #mA * us / 3.6 -> pAh
            previous_time = current_time
            global_buffer.append(f"{current_time/1_000:.3f}, {sin_current:.2f}, {global_last_current:.3f}, {global_last_voltage:.2f}, {x_freq:.3f}, {global_energy/1_000_000:.3f} \n")
            
            if len(global_buffer) >= global_buffer_size:
                print("DC buffer save occured during critical section!")
                sd_control.log_to_sd(global_filename)
        
        io_control.set_current(0)
        if global_buffer:
            sd_control.log_to_sd(global_filename)

def eis_continous(current, min_freq, max_freq):
    #freq_list, est_time = descending_log_list(min_freq, max_freq, 100)
    #print(f"DC EIS started {current}mA, {est_time}s")
    global global_energy, global_filename, global_buffer_size, global_buffer, global_last_voltage, global_last_current
    print("Started continous EIS")
    #max_frequency = 100.0 #Hz
    #min_frequency = 1   #Hz
    time_us = 40_000_000
    T = 1.2 
    c = max_freq/T
    io_control.set_current(0)
    start_time = extended_ticks_us.global_time_tracker.ticks_us()
    end_time = start_time + time_us 
    previous_time =extended_ticks_us.global_time_tracker.ticks_us()
    while extended_ticks_us.global_time_tracker.ticks_us() < end_time:
        relative_time = float((extended_ticks_us.global_time_tracker.ticks_us() - start_time)/1_000_000)
        sin_current = current * 0.5 * (1 + math.sin(2*math.pi*(c/(math.pow(relative_time,2)+0.1*max_freq))))
        io_control.set_current(sin_current)
        read_ADS1265()
        current_time = extended_ticks_us.global_time_tracker.ticks_us()
        global_energy += int(global_last_current*(current_time - previous_time)/3.6) #mA * us / 3.6 -> pAh
        previous_time = current_time
        #elapsed_time = time.ticks_diff(time.ticks_us(), start_time)
        global_buffer.append(f"{current_time/1_000:.3f}, {sin_current:.2f}, {global_last_current:.3f}, {global_last_voltage:.2f}, 1, {global_energy/1_000_000:.3f} \n")
        
        if len(global_buffer) >= global_buffer_size:
            print("DC buffer save occured during critical section!")
            sd_control.log_to_sd(global_filename)
    
    io_control.set_current(0)
    if global_buffer:
        sd_control.log_to_sd(global_filename)
    

def discharge_program(l_time, l_current, h_time, h_current, eis_current, min_freq, max_freq, repetitions, log_downsample):
    print("DC Discharge started")
    global  global_is_in_progress, global_filename, global_buffer, global_loop_iteration
    global_is_in_progress = 1

    global_filename = sd_control.get_new_filename()
    #log_to_sd(filename, ["Time [ms], I set[mA], I meas[mA], U meas[V], E [uAh]\n"])  # Nagłówek pliku
    
    extended_ticks_us.global_time_tracker.set_offset(extended_ticks_us.global_time_tracker.ticks_us())


    discharge(0, 5_000_000, log_downsample)

    for i in range(repetitions):

        discharge(h_current, h_time, log_downsample)
        display.display_disharge_status()

        discharge(l_current, l_time, log_downsample)
        display.display_disharge_status()

        eis(eis_current, min_freq, max_freq)
        #eis_continous(eis_current, min_freq, max_freq)
        display.display_disharge_status()

        global_loop_iteration = global_loop_iteration + 1

    global_is_in_progress = 0 
    print("DC Discharge finished")
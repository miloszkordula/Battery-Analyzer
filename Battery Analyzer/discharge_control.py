import io_control
import sd_control
import math
import extended_ticks_us
import display
import time


### Global variables ###
global_energy = int(0)
global_filename = ""
global_loop_iteration = int(0)
global_is_in_progress = int(0)
global_last_voltage = int(0)
global_last_current = int(0)
global_freq = float(0)


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

    times = []
    log_downsample_list = []
    
    est_overall_time = 0
    for x in values:
        log_downsample = 1
        while x * log_downsample < 0.125:
            log_downsample = log_downsample + 1
        log_downsample_list.append(log_downsample)

        est_time = max(2_000_000, min((3_000_000 / x), 16_000_000*log_downsample))
        times.append(est_time)

        est_overall_time = est_overall_time + (est_time/1_000_000)
    return values, times, log_downsample_list, est_overall_time



def discharge(current, time_us, log_downsample):
    print(f"DC Constant discharge started {current}mA, {time_us/1_000_000:.3f}s")
    global global_energy, global_filename, sd_control, global_last_voltage, global_last_current, global_loop_iteration
    io_control.set_current(current)
    start_time = extended_ticks_us.global_time_tracker.ticks_us()
    end_time = start_time + time_us 
    previous_time = extended_ticks_us.global_time_tracker.ticks_us()
    downsample_tracker = 0

    while extended_ticks_us.global_time_tracker.ticks_us() < end_time:
        read_ADS1265()
        current_time = extended_ticks_us.global_time_tracker.ticks_us()
    
        global_energy += int(global_last_current*(current_time - previous_time) / 36_000) #0.1uA * us / 36000 -> pAh
        previous_time = current_time
        #elapsed_time = time.ticks_diff(time.ticks_us(), start_time)
        if downsample_tracker >= log_downsample:
            sd_control.store_record(current_time, current, global_last_current, global_last_voltage, 0, global_energy, global_loop_iteration)
            #global_buffer.append(f"{current_time/1_000:.2f}, {current:.2f}, {global_last_current:.3f}, {global_last_voltage:.2f}, 0, {global_energy/1_000_000:.2f}, {global_loop_iteration} \n")
            downsample_tracker = 0
        downsample_tracker = downsample_tracker + 1
        
        if sd_control.global_current_index >= sd_control.global_buffer_size:
            print(f"SD saving {sd_control.global_current_index} records, avg {sd_control.global_current_index*1_000_000/time_us} SPS")
            sd_control.log_to_sd(global_filename)
            display.display_disharge_status()
    
    if sd_control.global_current_index:
        print(f"SD saving {sd_control.global_current_index} records, avg {sd_control.global_current_index*1_000_000/time_us} SPS")
        sd_control.log_to_sd(global_filename)
    display.display_disharge_status()


def eis(current, min_freq, max_freq, measurement_points):
    freq_list, time_list, log_downsample_list, est_time = descending_log_list(min_freq, max_freq, measurement_points)
    print(f"DC EIS started {current}mA, {est_time}s")
    global global_energy, global_filename, sd_control, global_last_voltage, global_last_current, global_loop_iteration, global_freq
    

    T = 1.2 
    c = max_freq/T

    previous_time = extended_ticks_us.global_time_tracker.ticks_us()


    for i, x_freq  in enumerate(freq_list):
        global_freq = x_freq
        io_control.set_current(0)
        print(f"DC Starting with f: {x_freq}, t:{time_list[i]/1_000_000}s log ds: {log_downsample_list[i]}")
        inner_start_time = extended_ticks_us.global_time_tracker.ticks_us()
        
        log_downsample = log_downsample_list[i]
       # while x_freq * log_downsample < 0.125:
      #     log_downsample = log_downsample + 1

        #inner_end_time = inner_start_time + max(2_000_000, min((3_000_000 / x_freq), 16_000_000*log_downsample))
        inner_end_time = inner_start_time + time_list[i]
        sine_const = 2 * math.pi * x_freq / 1_000_000

        previous_voltage = 0
        resample_counter = 0
        downsample_tracker = 1

        while extended_ticks_us.global_time_tracker.ticks_us() < inner_end_time:
            current_inner_time = extended_ticks_us.global_time_tracker.ticks_us() - inner_start_time
            sin_current = current * 0.5 * (1 + math.sin(sine_const * current_inner_time))
            io_control.set_current(sin_current)
            read_ADS1265()

            while previous_voltage != 0 and abs(previous_voltage - global_last_voltage) > 4_000_0 and resample_counter < 50: #0.1uV
                if resample_counter == 0 or resample_counter == 49:
                    print(f"ADS V diff {(previous_voltage - global_last_voltage)/10_000:.3f}mV!")
                time.sleep_us(500)
                read_ADS1265()   
                resample_counter = resample_counter + 1
            resample_counter = 0   
            previous_voltage = global_last_voltage

            current_time = extended_ticks_us.global_time_tracker.ticks_us()
            global_energy += int(global_last_current*(current_time - previous_time) / 36_000) #0.1uA * us / 36000 -> pAh
            previous_time = current_time
    
            if downsample_tracker < log_downsample:
                downsample_tracker = downsample_tracker + 1
                time.sleep_ms(3)
            else:
                sd_control.store_record(current_time, sin_current, global_last_current, global_last_voltage, x_freq, global_energy, global_loop_iteration)
                downsample_tracker = 1
                
            if sd_control.global_current_index >= sd_control.global_buffer_size:
                sd_control.log_to_sd(global_filename)
                print("DC buffer save occured during critical section!")
                display.display_disharge_status()
    
        if sd_control.global_current_index:
            print(f"SD saving {sd_control.global_current_index} records, avg {sd_control.global_current_index*1_000_000/time_list[i]} SPS")
            sd_control.log_to_sd(global_filename)

        display.display_disharge_status()
    global_freq = 0


    
import settings

def discharge_program():#l_time, l_current, h_time, h_current, eis_current, min_freq, max_freq, repetitions, log_downsample, measurement_points):
    print("DC Discharge started")
    global  global_is_in_progress, global_filename, global_loop_iteration
    global_is_in_progress = 1

    global_filename = sd_control.get_new_filename()
    #global_buffer.append("Time [ms], I set[mA], I meas[mA], U meas[V], f[Hz],  E [uAh], i\n")  # Nagłówek pliku
    
    extended_ticks_us.global_time_tracker.set_offset(extended_ticks_us.global_time_tracker.ticks_us())


    discharge(0, 5_000_000, 10)

    loaded_settings = settings.Settings() 

    for i in range(loaded_settings.repetitions):

        loaded_settings.Program()

        global_loop_iteration = global_loop_iteration + 1

    global_is_in_progress = 0 
    print("DC Discharge finished")
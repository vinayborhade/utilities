import os
import pandas as pd
from time import sleep

def split_entire_video(path, file_name, chunk_size):
    # splits entire video into multiple chunks of intervals specified
    if file_name.endswith(".mp4"): 
        command = "ffmpeg -fflags +discardcorrupt -i " + os.path.join(path, file_name) + "-vf 'setpts=PTS-STARTPTS+0' -c copy -map 0 -segment_time " + chunk_size +  " -f segment -reset_timestamps 1 " + os.path.join(path, "output%03d.mp4")
        os.system(command)

def cut_video_st_end_time(path, file_name, st, end, out_file):

    # cuts video to give simgle file for start and end times specified
    if file_name.endswith(".mp4"): 
        command = "ffmpeg -ss " + st + " -i " + os.path.join(path, file_name) + " -c copy -to "+ end + " " + out_file
        os.system(command)


def remove_silence_add_pauses(path, file_name):
    if file_name.endswith(".mp4"): 
        command = "ffmpeg -i " + os.path.join(path, file_name) + " -af silenceremove=start_periods=1:stop_periods=-1:start_threshold=-60dB:stop_threshold=-60dB:start_silence=1:stop_silence=1 outputfile.mp3"
        os.system(command)

def detect_silence(path, file_name):
    if file_name.endswith(".mp4"): 
        command = "ffmpeg -i " + os.path.join(path, file_name) + " -nostats -af silencedetect=n=-50dB:d=3 -f null - 2> silence.txt"
        os.system(command)
    
def get_df_from_silence_txt(output_file):
    # Read the output from the file
    with open(output_file, 'r') as file:
        output = file.read()

    # Parse the output
    data = []
    current_start = None

    for line in output.splitlines():
        if 'silence_start' in line:
            current_start = line.split()[-1]
        elif 'silence_end' in line:
            if current_start:
                end_time = line.split()[-1]
                data.append({'start': current_start, 'silence_duration': end_time})
                current_start = None

    # Convert to DataFrame
    df = pd.DataFrame(data)

    return df
    
def main():
    path = r'D:\Projects\utilities'
    orig_file_name = r'Career_Opportunities_In_AI.mp4'

    chunk_size = r'00:05:00'
    # split_entire_video(path, orig_file_name, chunk_size)

    st_time = r'00:05:00'
    end_time = r'00:10:00'
    chunk_out_file = "output_" + st_time.replace(":","-") + "_" + end_time.replace(":","-") + ".mp4"
    # cut_video_st_end_time(path, orig_file_name, st_time, end_time, chunk_out_file)

    sleep(1)
    # remove_silence_add_pauses(path, chunk_out_file)


    # detect_silence(path, file_name = chunk_out_file)

    # detect_silence(path, file_name = orig_file_name)

    silence_file = "silence.txt"
    df = get_df_from_silence_txt(silence_file)
    df['start'] = df['start'].astype(float)
    df['silence_duration'] = df['silence_duration'].astype(float)
    df['silence_end'] = df['start'] + df['silence_duration']
    # print(df)

    # Initialize list for non-silence periods
    non_silence_periods = []

    # Define the start and end of the video (assumed values for illustration)
    start_of_video = 0
    end_of_video = df['silence_end'].max() + 1  # Assume an extra 1 seconds after the last silence for this example

    # Find non-silence periods between silences
    previous_silence_end = start_of_video

    for index, row in df.iterrows():
        if row['start'] > previous_silence_end:
            non_silence_periods.append({
                'start': previous_silence_end,
                'end': row['start']
            })
        
        # Update the end of the previous silence to the current silence end
        previous_silence_end = row['silence_end']

    # Add period after the last silence
    if previous_silence_end < end_of_video:
        non_silence_periods.append({
            'start': previous_silence_end,
            'end': end_of_video
        })

    # Convert to DataFrame
    non_silence_df = pd.DataFrame(non_silence_periods)
    non_silence_df['start'] = non_silence_df['start'].astype(float)
    non_silence_df['end'] = non_silence_df['end'].astype(float)
    non_silence_df['duration'] = non_silence_df['end'] - non_silence_df['start']
    non_silence_df['file_name'] = orig_file_name
    # print(non_silence_df)
    non_silence_df.to_csv('non_silence.csv')

if __name__ == '__main__':
    main()
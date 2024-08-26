import os
import math
import pandas as pd
from time import sleep
import datetime

def split_entire_video(path, file_name, chunk_size):
    # splits entire video into multiple chunks of intervals specified
    if file_name.endswith(".mp4"): 
        command = "ffmpeg -fflags +discardcorrupt -i " + os.path.join(path, file_name) + "-vf 'setpts=PTS-STARTPTS+0' -c copy -map 0 -segment_time " + chunk_size +  " -f segment -reset_timestamps 1 " + os.path.join(path, "output%03d.mp4")
        os.system(command)

def convert_seconds_to_hhmmss(seconds):
    td = datetime.timedelta(seconds=seconds)
    # Extract hours, minutes, and seconds from the timedelta object
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    # Format as hh:mm:ss
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def cut_video_st_duration_time(path, file_name, st_sec, duration, out_file):

    # print(out_file, st_sec, duration)

    # cuts video to give simgle file for start and end times specified
    if file_name.endswith(".mp4"): 
        # command = f"ffmpeg -i \"{os.path.join(path, file_name)}\" -ss {math.floor(st_sec)} -t {math.ceil(duration)} -c copy \"{out_file}\""
        command = f"ffmpeg -i \"{os.path.join(path, file_name)}\" -ss {math.floor(st_sec)} -t {math.ceil(duration)} -c:v libx264 -c:a aac \"{out_file}\""
    
        os.system(command)

def cut_video_st_end_time(path, file_name, st_sec, end_sec, out_file):

    # print(out_file, st_sec, end_sec)

    # cuts video to give simgle file for start and end times specified
    if file_name.endswith(".mp4"): 
        command = f"ffmpeg -i \"{os.path.join(path, file_name)}\" -ss {str(st_sec)} -to {str(end_sec)} -c copy \"{out_file}\""
    
        # command = "ffmpeg -ss " + str(st_sec) + " -i " + os.path.join(path, file_name) + " -c copy -to "+ str(end_sec) + " " + out_file
        
        os.system(command)


def remove_silence_add_pauses(path, file_name):
    if file_name.endswith(".mp4"): 
        command = "ffmpeg -i " + os.path.join(path, file_name) + " -af silenceremove=start_periods=1:stop_periods=-1:start_threshold=-60dB:stop_threshold=-60dB:start_silence=1:stop_silence=1 outputfile.mp3"
        os.system(command)

def detect_silence(path, file_name):

    output_file = f'Silences_{file_name}.txt'
    output_file_path = os.path.join(path, output_file)

    if file_name.endswith(".mp4"): 
        command = "ffmpeg -i " + os.path.join(path, file_name) + " -nostats -af silencedetect=n=-50dB:d=3 -f null - 2> " + output_file_path
        os.system(command)
    
def get_df_from_silence_txt(path, file_name):
    output_file = f'Silences_{file_name}.txt'
    output_file_path = os.path.join(path, output_file)
    # Read the output from the file
    with open(output_file_path, 'r') as file:
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

def generate_non_silence_time(orig_file_name, silence_file = "silence.txt"):
    
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
    return non_silence_df

def join_clips():
    pass
    # ffmpeg -fflags +genpts+igndts -f concat -safe 0 -segment_time_metadata 1 -i vidlist.txt -c:v copy -af aselect=concatdec_select,aresample=async=1 output.mp4
    
def generate_clips_for_non_silence_time(video_path, non_silence_time_df):
    # Iterate over each row in the DataFrame and generate clips
    for index, row in non_silence_time_df.iterrows():
        start_sec = row['start']
        duration = row['duration']
        file_name = row['file_name']
        
        # Construct output file name for the clip
        output_file = f"{os.path.splitext(file_name)[0]}_{start_sec}_{duration}.mp4"

        output_file_path = os.path.join(video_path, output_file)

        # Call the function to cut the video
        sleep(1)
        cut_video_st_duration_time(video_path, file_name, start_sec, duration, output_file_path)

# Function to convert hh:mm:ss to seconds
def time_to_seconds(time_str):
    # print(time_str, type(time_str))
    h, m, s = map(int, time_str.split(':'))
    return h * 3600 + m * 60 + s

def generate_clips_for_custom_split_time(video_path, custom_split_time_df):
    # Apply the function to calculate duration
    custom_split_time_df['start_sec'] = custom_split_time_df['start'].apply(time_to_seconds)
    custom_split_time_df['end_sec'] = custom_split_time_df['end'].apply(time_to_seconds)
    custom_split_time_df['duration_sec'] = custom_split_time_df['end_sec'] - custom_split_time_df['start_sec']

    for index, row in custom_split_time_df.iterrows():
        start_sec = row['start_sec']
        duration = row['duration_sec']
        file_name = row['file_name']
        topic = row['topic']

        
        # Construct output file name for the clip
        output_file = f"{topic}.mp4"

        output_file_path = os.path.join(video_path, output_file)    
        
        sleep(1)
        # cut_video_st_end_time(video_path, file_name, start_sec, end_sec, output_file_path)
        cut_video_st_duration_time(video_path, file_name, start_sec, duration, output_file_path)

def generate_silences_df_for_clips(path, clip_names):
    df_lst = []
    for clip_name in clip_names:
        df = get_df_from_silence_txt(path, file_name = clip_name + ".mp4")
        df['file_name'] = clip_name
        df_lst.append(df)
    df_silences = pd.concat(df_lst)
    return df_silences

def detect_silences_all_clips(path, clip_names):
    for clip_name in clip_names:
        detect_silence(path, file_name = clip_name + ".mp4")

def speed_audio_video_all_clips(path, clip_names):
    for clip_name in clip_names:
        speed_audio_video(path, file_name = clip_name + ".mp4")

def speed_audio_video(path, file_name):
    output_file = f'speedup_{file_name}'
    output_file_path = os.path.join(path, output_file)

    if file_name.endswith(".mp4"): 
        command = 'ffmpeg -i ' + os.path.join(path, file_name) + ' -vf "setpts=0.8*PTS" -af "atempo=1.25" ' + output_file_path
        os.system(command)

def image_overaly(path, file_name, image_name):
    output_file = f'overlay_{file_name}'
    output_file_path = os.path.join(path, output_file)

    if file_name.endswith(".mp4"): 
        command = 'ffmpeg -i ' + os.path.join(path, file_name) + ' -i ' + os.path.join(path, image_name) + ' -filter_complex "overlay=210:110" ' +  output_file_path
        os.system(command)
    
    
def main():
    path = r'D:\Projects\training_videos\Career_Opportunities_In_AI'
    
    orig_file_name = r'Career_Opportunities_In_AI.mp4'

    chunk_size = r'00:05:00'
    # split_entire_video(path, orig_file_name, chunk_size)

    # st_time = 978.647438
    # end_time = 500.78

    # chunk_out_file = "output_" + str(st_time) + "_" + str(end_time) + ".mp4"
    # cut_video_st_end_time(path, orig_file_name, st_time, end_time, chunk_out_file)

    # sleep(1)
    # remove_silence_add_pauses(path, chunk_out_file)

    # clip_names = ['What_Is_AI','Job_Profiles_In_AI','Career_Paths','Skills_Required_For_AI','AI_Use_Cases_In_Industry','Challenges_In_AI_Career_And_How_To_Overcome','Key_Takaways_For_Making_Career_In_AI','AI_Industry_Usage','About_Dataastaa_And_Our_Vision']
    # detect_silences_all_clips(path, clip_names)
        
    # df_silences = generate_silences_df_for_clips(path, clip_names)
    # silences_df_path = os.path.join(r'D:\Projects\training_videos\Career_Opportunities_In_AI', r'All_Clip_Silences.csv')
    # df_silences.to_csv(silences_df_path)

 
    # detect_silence(path, file_name = orig_file_name)

    # non_silence_time_df = generate_non_silence_time(orig_file_name)
    # non_silence_time_df.to_csv('non_silence.csv')

    # non_silence_csv_path = os.path.join(r'D:\Projects\utilities', r'non_silence.csv')
    # non_silence_time_df = pd.read_csv(non_silence_csv_path)
    # non_silence_time_df['output_file'] = None
    # video_path = path
    # generate_clips_for_non_silence_time(video_path, non_silence_time_df)

    custom_split_csv_path = os.path.join(r'D:\Projects\training_videos\Career_Opportunities_In_AI', r'Career_Paths.csv')
    custom_split_df = pd.read_csv(custom_split_csv_path)
    video_path = path
    generate_clips_for_custom_split_time(video_path, custom_split_df)

    # clip_names = ['What_Is_AI','Job_Profiles_In_AI','Career_Paths','Skills_Required_For_AI','AI_Use_Cases_In_Industry','Challenges_In_AI_Career_And_How_To_Overcome','Key_Takaways_For_Making_Career_In_AI','AI_Industry_Usage','About_Dataastaa_And_Our_Vision']
    # speed_audio_video_all_clips(path, clip_names)

    # video_name = 'Neural_Network_And_Resurgence_Of_AI.mp4'
    # overlay_image = 'NN_overlay.png'
    # image_overaly(path, video_name, overlay_image)


if __name__ == '__main__':
    main()
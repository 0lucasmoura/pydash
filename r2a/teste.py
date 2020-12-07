import numpy as np
import time


um = np.array([np.log(bitrate/list_bitrates[0]) for bitrate in list_bitrates])
rebuf_avoid_level = 5

for ix, segment in enumerate(segments_of_video):
    t = min(video_current_playtime, video_total_playtime - video_current_playtime)
    t2 = max(t/2, 3 * segment_time)

    dinamic_buffer = min(max_buffer_size, t2/segment_time)
    dinamic_control_param_list = (dinamic_buffer - 1)/ \
                                (um + rebuf_avoid_level*segment_time)

    iq = np.argmax(dinamic_control_param_list * um + dinamic_control_param_list*rebuf_avoid_level*segment_time - current_buffer_size)/list_bitrates

    ix_anterior = iq - 1 if iq > 0 else 0

    if iq > um[ix_anterior]:
        m_filter = list_bitrates/segment_time <= max(bandwidth_anterior,list_bitrates[0]/segment_time)
        m = np.where(np.any(m_filter, axis=1))[-1]
        if m < um[ix_anterior]:
            iq = um[ix_anterior]
        else:  # BOLA-U
            iq = iq + 1 if iq < len(um) else iq

    time.sleep(max(current_buffer_size - dinamic_buffer, 0))

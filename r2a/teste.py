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


        if qi >= self.qi_anterior:
            m_2 = len(self.qi_array) - 1
            while True:
                m_filter = self.qi_array/self.segment_time <= max(self.bandwith_anterior, self.qi_array[0]/self.segment_time)
                m_1 = self.qi_array[m_filter][-1]
                m_1 = np.where(self.qi_array == m_1)[0][0]
                print(m_filter)
                if m_1 >= qi:
                    qi = m_1
                elif m_1 < self.qi_anterior:
                    qi = self.qi_anterior

                ql_m1 = (dinamic_control_param_list * self.quality_score_array[m_1]) + (dinamic_control_param_list * self.rebuf_avoid_level * self.segment_time) - current_buffer_size/self.qi_array[m_1]
                ql_m2 = (dinamic_control_param_list * self.quality_score_array[m_2]) + (dinamic_control_param_list * self.rebuf_avoid_level * self.segment_time) - current_buffer_size/self.qi_array[m_2]

                if np.all(ql_m1 >= ql_m2):
                    break
                else:
                    m_2 = m_1

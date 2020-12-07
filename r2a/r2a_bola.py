from r2a.ir2a import IR2A
from player.parser import *
from player.player import Player
import time
import numpy as np
from datetime import datetime
from base.configuration_parser import ConfigurationParser

player = Player.get_instance()


class R2A_BOLA(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.quality_score_array = []
        self.rebuf_avoid_level = 5
        self.request_time = 0
        self.qi_array = []
        self.video_total_playtime = 0
        self.video_current_playtime = 0
        self.segment_time = 0
        self.max_buffer_size = player.max_buffer_size
        self.bandwith_anterior = 0
        self.qi_anterior = 0

    def handle_xml_request(self, msg):
        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):

        parsed_mpd = parse_mpd(msg.get_payload())   # index : valor bitrate

        self.qi_array = np.array(parsed_mpd.get_qi())
        # pega o tamanho total do video em segundos
        self.video_total_playtime = get_total_video_playtime_from_mpd(parsed_mpd.get_period_info()["duration"][2:])
        # instancia o array de qualidade do BOLA usando uma função LOG tal qual demonstrado no paper
        self.quality_score_array = np.array([np.log(bitrate/self.qi_array[0]) for bitrate in self.qi_array])
        # estima um bandwidth de acordo com o download do xml
        self.bandwith_anterior = msg.get_bit_length() / (time.perf_counter() - self.request_time )

        self.send_up(msg)

    def handle_segment_size_request(self, msg):

        self.segment_time = msg.get_segment_size()

        # tempos de inicio e fim para o BOLA-FINITE
        t = min(player.buffer_played, self.video_total_playtime - player.buffer_played)
        t2 = max(t/2, 3 * self.segment_time)

        dinamic_buffer = min(self.max_buffer_size, t2/self.segment_time)
        dinamic_control_param_list = (dinamic_buffer - 1)/(self.quality_score_array + (self.rebuf_avoid_level * self.segment_time))

        # TODO - Fix Player Class as a Singleton so that we can acces the instance atributes with no problems
        # Pega o tamanho atual do buffer
        current_buffer_size = player.get_amount_of_video_to_play_without_lock()

        # pega o index do bitrate qi a ser utilizado! Referente a linha 6 do algoritmo proposto no paper
        qi = np.argmax((((dinamic_control_param_list * self.quality_score_array[self.qi_anterior]) + 
                                    (dinamic_control_param_list * self.rebuf_avoid_level * self.segment_time) - current_buffer_size)/self.qi_array[self.qi_anterior]))
        
        # faz as decisões entre os diversos qis de acordo com a bandwidth dos downloads anteriores
        if qi >= self.qi_anterior:
            m_filter = self.qi_array/self.segment_time <= max(self.bandwith_anterior, self.qi_array[0]/self.segment_time)
            m = self.qi_array[m_filter][-1]
            if m >= self.qi_array[qi]:
                qi = np.where(self.qi_array == m)[0][0]
            elif m < self.qi_array[self.qi_anterior]:
                qi = self.qi_anterior

        self.qi_anterior = qi

        # De acordo com a linha 21 do algoritmo proposto pelos autores, esperar x segundos para o esvaziamento da fila
        time.sleep(max((self.segment_time * (current_buffer_size - dinamic_buffer)), 0))

        msg.add_quality_id(self.qi_array[qi])

        self.request_time = time.perf_counter()
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        # estima um bandwidth de acordo com o download do segmento de video
        self.bandwith_anterior = msg.get_bit_length() / (time.perf_counter() - self.request_time)
        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        pass

def get_total_video_playtime_from_mpd(mpd):
        hours = float(mpd.split('H')[0])
        minutes = float(mpd.split('H')[1].split("M")[0])
        seconds = float(mpd.split('H')[1].split("M")[1].split("S")[0])
        return hours * 3600 + minutes * 60 + seconds

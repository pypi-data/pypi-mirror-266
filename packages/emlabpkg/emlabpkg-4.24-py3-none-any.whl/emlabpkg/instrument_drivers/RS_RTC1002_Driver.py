import numpy as np
from qcodes import VisaInstrument, InstrumentChannel
import qcodes.validators as vals
from time import time, sleep

class RTC1002(VisaInstrument):

    def __init__(self, name: str, address: str, **kwargs):
        
        super().__init__(name, address, terminator='\n', **kwargs)
        self.connect_message()

        self._initialize_submodules()

        self.add_parameter(
            "aver_count",
            get_cmd = 'acq:aver:coun?',
            get_parser = int,
            set_cmd = 'acq:aver:coun {}',
            set_parser = int,
            vals = vals.Ints(2, 1024),
            label = 'Averaging Counts'
        )

    def _initialize_submodules(self):
        for channel_num in [1, 2]:
            channel = RTC1002Channel(parent=self, channel_num=channel_num)
            self.add_submodule(channel._channel_name.lower(), channel)
        display = RTC1002Display(parent=self)
        gen_func = RTC1002GeneratorFunction(parent=self)
        self.add_submodule('display', display)
        self.add_submodule('generator_function', gen_func)
    
    def reset(self):
        self.write('*rst')
        self.submodules.clear()
        self._initialize_submodules()
    
    def autoscale(self):
        self.write('aut')
        sleep(2)
        self.ch1.get_trace_parameters()
        self.ch2.get_trace_parameters()

class RTC1002Channel(InstrumentChannel):
    
    def __init__(self, parent: RTC1002, channel_num: int) -> None:
        
        self._channel_num = channel_num
        self._channel_name = f"Ch{self._channel_num}"
        
        super().__init__(parent, self._channel_name)

        self.add_parameter(
            "state",
            get_cmd = f'chan{self._channel_num}:stat?',
            get_parser = self._get_state_parser,
            set_cmd = f'chan{self._channel_num}:stat {{}}',
            set_parser = self._set_state_parser,
            vals = vals.Bool(),
            label = 'Channel State'
        )
        
        self.add_parameter(
            "coupling_type",
            get_cmd = f'chan{self._channel_num}:coup?',
            get_parser = str,
            set_cmd = f'chan{self._channel_num}:coup {{}}',
            set_parser = str,
            vals = vals.Enum('DCL', 'ACL', 'GND'),
            label = 'Channel Coupling Type'
        )

        self.add_parameter(
            "label",
            get_cmd = f'chan{self._channel_num}:lab?',
            get_parser = str,
            set_cmd = f'chan{self._channel_num}:lab {{}}',
            set_parser = str,
            label = 'Channel Label'
        )

        self.add_parameter(
            "label_state",
            get_cmd = f'chan{self._channel_num}:lab:stat?',
            get_parser = self._get_state_parser,
            set_cmd = f'chan{self._channel_num}:lab:stat {{}}',
            set_parser = self._set_state_parser,
            vals = vals.Bool(),
            label = 'Channel Label State'
        )

        self.add_parameter(
            "voltage_yscale",
            get_cmd = f'chan{self._channel_num}:scal?',
            get_parser = float,
            set_cmd = f'chan{self._channel_num}:scal {{}}',
            set_parser = float,
            label = 'Channel Voltage Vertical Scale'
        )

        self.add_parameter(
            "bandwidth",
            get_cmd = f'chan{self._channel_num}:band?',
            get_parser = str,
            set_cmd = f'chan{self._channel_num}:band {{}}',
            set_parser = str,
            vals = vals.Enum('FULL', 'B20'),
            label = 'Channel Bandwidth Limit'
        )

        self.add_parameter(
            "trace_data",
            get_cmd = f'chan{self._channel_num}:data?',
            get_parser = self._raw_trace_data_parser,
            label = 'Channel Trace Data'
        )

        self.get_trace_parameters()

    def get_trace_parameters(self):
        self.state(True)
        sleep(0.5)
        raw_data_header = self.ask(f'chan{self._channel_num}:data:head?')
        data_header = [float(val) for val in raw_data_header.split(',')]
        self._x_start = data_header[0]
        self._x_stop = data_header[1]
        self._sample_len = int(data_header[2])
        self._num_vals_per_interval = int(data_header[3])
        self._setpoints = np.linspace(self._x_start, self._x_stop, self._sample_len)
        try:
            self._x_inc = self._setpoints[1] - self._setpoints[0]
        except IndexError:
            self._x_inc = np.nan

    def _get_state_parser(self, state):
        if state == '0':
            return False
        else:
            return True
        
    def _set_state_parser(self, state):
        if state:
            return '1'
        else:
            return '0'

    def _raw_trace_data_parser(self, raw_data):
        data = list(map(float, raw_data.split(',')))
        return data
    
class RTC1002Display(InstrumentChannel):
    
    def __init__(self, parent: RTC1002) -> None:

        super().__init__(parent, 'display')

    def send_message_dialog(self, message: str, time: float = 5):
        self.write(f"disp:dial:mess '{message}'")
        sleep(time)
        self.close_message_dialog()

    def close_message_dialog(self):
        self.write('disp:dial:clos')

class RTC1002GeneratorFunction(InstrumentChannel):
    
    def __init__(self, parent: RTC1002) -> None:

        super().__init__(parent, 'generator_function')
        
        self.add_parameter(
            "type",
            get_cmd = 'gen:func?',
            get_parser = str,
            set_cmd = 'gen:func {}',
            set_parser = str,
            vals = vals.Enum('DC', 'SIN', 'SQU', 'PULS', 'TRI', 'RAMP'),
            label = 'Type of Output Function'
        )

        self.add_parameter(
            "amplitude",
            get_cmd = 'gen:volt?',
            get_parser = float,
            set_cmd = 'gen:volt {}',
            set_parser = float,
            vals = vals.Numbers(6e-2, 6),
            label = 'Amplitude of Output Function'
        )

        self.add_parameter(
            "dc_offset",
            get_cmd = 'gen:volt:offs?',
            get_parser = float,
            set_cmd = 'gen:volt:offs {}',
            set_parser = float,
            vals = vals.Numbers(-3, 3),
            label = 'DC Offset of Output Function'
        )

        self.add_parameter(
            "frequency",
            get_cmd = 'gen:freq?',
            get_parser = float,
            set_cmd = 'gen:freq {}',
            set_parser = float,
            vals = vals.Numbers(1e-1, 5e4),
            label = 'Frequency of Output Function'
        )

        self.add_parameter(
            "state",
            get_cmd = 'gen:outp?',
            get_parser = self._get_state_parser,
            set_cmd = 'gen:outp {}',
            set_parser = self._set_state_parser,
            vals = vals.Bool(),
            label = 'State of Output Function'
        )

    def _get_state_parser(self, state):
        if state == '0':
            return False
        else:
            return True
        
    def _set_state_parser(self, state):
        if state:
            return '1'
        else:
            return '0'

    def send_message_dialog(self, message: str, time: float = 5):
        self.write(f"disp:dial:mess '{message}'")
        sleep(time)
        self.close_message_dialog()

    def close_message_dialog(self):
        self.write('disp:dial:clos')

class RTC1002Arithmetics(InstrumentChannel):
    
    def __init__(self, parent: RTC1002) -> None:

        super().__init__(parent, 'arithmetics')

        self.add_parameter(
            "mode",
            get_cmd = f'chan{self._channel_num}:arit?',
            get_parser = str,
            set_cmd = f'chan{self._channel_num}:arit {{}}',
            set_parser = str,
            vals = vals.Enum('OFF', 'ENV', 'AVER', 'FILT'),
            label = 'Mode for FFT Calculation and Display'
        )

        self.add_parameter(
            "freq_center",
            get_cmd = 'calc:math:fft:cfr?',
            get_parser = float,
            set_cmd = 'calc:math:fft:cfr {}',
            set_parser = float,
            label = 'Center Frequency for FFT'
        )

        self.add_parameter(
            "freq_span",
            get_cmd = 'calc:math:fft:span?',
            get_parser = float,
            set_cmd = 'calc:math:fft:span {}',
            set_parser = float,
            label = 'Span of Frequency for FFT'
        )
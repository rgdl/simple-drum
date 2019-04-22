import tkinter as tk

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
matplotlib.use("TkAgg")

from drums import BassDrum


class DrumTesterGUI(tk.Tk):
    PACK_PARAMS = {
        'PLAY_BUTTON': {'side': tk.RIGHT},
        'PARAMETER_CONTROLS': {'side': tk.RIGHT},
        'GRAPH': {'side': tk.TOP, 'fill': tk.BOTH, 'expand': 1},
    }

    TITLE = 'Drum Tester'

    GEOMETRY = '800x500+100+100'

    N_SLIDER_INCREMENTS = 1000

    def _get_play_button(self):
        tk.Button(self.frame, text='Play', command=self.drum.play).pack(**self.PACK_PARAMS['PLAY_BUTTON'])

    def _get_parameter_controls(self):
        drum_params = self.drum.params
        parameter_controls_frame = tk.Frame(self.frame)
        parameter_controls_frame.pack(**self.PACK_PARAMS['PARAMETER_CONTROLS'])

        for param, value in drum_params.items():
            param_range = self.drum.parameter_ranges[param]

            def callback_factory(scale_param):
                def func(new_value):
                    self.drum.update_sample({scale_param: float(new_value)})
                    self._draw_graph()
                return func

            slider = tk.Scale(
                parameter_controls_frame,
                label=param,
                from_=param_range[0],
                to=param_range[1],
                resolution=(param_range[1] - param_range[0]) / self.N_SLIDER_INCREMENTS,
                orient=tk.HORIZONTAL,
                command=callback_factory(param),
            )

            # This has param=final value every time the command runs
            slider.set(value)
            slider.pack(side=tk.LEFT)

    def _draw_graph(self):
        self.ax.clear()
        self.ax.plot(self.drum.T, self.drum.sample, label='Waveform')

        for envelope_name, envelope_values in self.drum.envelopes.items():
            normalised_enevelope_values = self.drum.sample.max() * envelope_values / envelope_values.max()
            self.ax.plot(self.drum.T, normalised_enevelope_values, label=envelope_name)

            self.ax.legend()
        self.canvas.draw()

    def _get_graph(self):
        # Make plot
        fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
        self.ax = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig, master=self)

        self._draw_graph()

        self.canvas.get_tk_widget().pack(**self.PACK_PARAMS['GRAPH'])

        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        self.canvas.get_tk_widget().pack(**self.PACK_PARAMS['GRAPH'])

    def __init__(self, drum, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.drum = drum()

        # Create frame
        self.wm_title(self.TITLE)
        self.geometry(self.GEOMETRY)
        self.frame = tk.Frame(self)
        self.frame.pack()

        # Create UI components
        self._get_play_button()
        self._get_parameter_controls()
        self._get_graph()

        # Focus on GUI window by default
        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(self.attributes, '-topmost', False)

        # Run loop and catch the inertial scroll error if it happens
        while True:
            try:
                self.mainloop()
                break
            except UnicodeDecodeError:
                pass


if __name__ == '__main__':
    DrumTesterGUI(BassDrum)

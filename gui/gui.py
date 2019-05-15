import tkinter as tk


class GUI(tk.Tk):
    PACK_PARAMS = {
        'PLAY_BUTTON': {'side': tk.RIGHT},
        'PARAMETER_CONTROLS': {'side': tk.RIGHT},
    }

    TITLE = 'Drum Tester'

    GEOMETRY = '800x500+100+100'

    N_SLIDER_INCREMENTS = 1000

    def _get_global_controls(self):
        frame = tk.Frame(self.frame, highlightbackground="green", highlightcolor="green", highlightthickness=1, width=500, height=100, bd= 0)
        frame.grid(column=0, row=1, columnspan=2, sticky='W')
        tk.Label(frame, text='Global Controls').pack()

    def _get_drum_controls(self):
        frame = tk.Frame(self.frame, highlightbackground="green", highlightcolor="green", highlightthickness=1, width=500, height=100, bd=0)
        frame.grid(column=0, row=0)
        tk.Label(frame, text='Drum Controls').pack(side=tk.TOP)
        for drum in range(3):
            tk.Label(frame, text=f'Drum {drum}').pack(side=tk.TOP)

    def _get_sequencer_grid(self):
        frame = tk.Frame(self.frame, highlightbackground="green", highlightcolor="green", highlightthickness=1,
                         width=500, height=100, bd=0)
        frame.grid(column=1, row=0)
        tk.Label(frame, text='Sequencer Grid').pack()

    # def _get_play_button(self):
    #     tk.Button(self.frame, text='Play', command=self.drum.play).pack(**self.PACK_PARAMS['PLAY_BUTTON'])

    # def _get_parameter_controls(self):
    #     drum_params = self.drum.params
    #     parameter_controls_frame = tk.Frame(self.frame)
    #     parameter_controls_frame.pack(**self.PACK_PARAMS['PARAMETER_CONTROLS'])
    #
    #     for param, value in drum_params.items():
    #         param_range = self.drum.parameter_ranges[param]
    #
    #         def callback_factory(scale_param):
    #             def func(new_value):
    #                 self.drum.update_sample({scale_param: float(new_value)})
    #                 self._draw_graph()
    #             return func
    #
    #         slider = tk.Scale(
    #             parameter_controls_frame,
    #             label=param,
    #             from_=param_range[0],
    #             to=param_range[1],
    #             resolution=(param_range[1] - param_range[0]) / self.N_SLIDER_INCREMENTS,
    #             orient=tk.HORIZONTAL,
    #             command=callback_factory(param),
    #         )
    #
    #         # This has param=final value every time the command runs
    #         slider.set(value)
    #         slider.pack(side=tk.LEFT)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create frame
        self.wm_title(self.TITLE)
        self.geometry(self.GEOMETRY)
        self.frame = tk.Frame(self)
        self.frame.pack()

        # Create UI components
        # self._get_play_button()
        # self._get_parameter_controls()
        # self._get_graph()

        # To line up drum controls with sequencer lanes, maybe everything above the global controls should be a grid?

        # For now:
        # - global controls across the bottom
        self._get_global_controls()
        # - drum controls on the left
        self._get_drum_controls()
        # - upper right is sequencer grid
        self._get_sequencer_grid()

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
    GUI()

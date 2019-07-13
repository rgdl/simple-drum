import tkinter as tk
from sequencer_gui_interface import SequencerEvent
from sequencer_gui_interface import SequencerGUIInterface

GRID_BACKGROUND_COLOUR = 'blue'
CELL_OFF_COLOUR = 'blue'
CELL_ON_COLOUR = 'green'
CELL_BORDER_COLOUR = 'white'
LANE_COLOUR = 'blue'
CURRENT_STEP_MARKER_COLOUR = 'yellow'

MIN_BPM = 20
MAX_BPM = 200

MIN_PULSES_PER_BEAT = 1
MAX_PULSES_PER_BEAT = 6

GLOBAL_SLIDER_WIDTH = 200


class GUI(tk.Tk):

    TITLE = 'Drum Machine'

    GEOMETRY = '800x500+100+100'

    N_SLIDER_INCREMENTS = 1000

    def __repr__(self):
        return f'Drum Machine GUI {id(self)}'

    def __init__(self, *args, **kwargs):
        self.sequencer_gui_interface = kwargs.pop('sequencer_gui_interface', None)

        super().__init__(*args, **kwargs)

        # Create frame
        self.wm_title(self.TITLE)
        self.geometry(self.GEOMETRY)
        self.frame = tk.Frame(self)
        self.frame.pack()

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

    def _push_event_to_sequencer(self, event: SequencerEvent):
        self.sequencer_gui_interface.push_to_sequencer_events_queue(event)

    def _get_global_controls(self):
        frame = tk.Frame(self.frame, highlightbackground="green", highlightcolor="green", highlightthickness=1, width=500, height=100, bd= 0)
        frame.grid(column=0, row=1, columnspan=2, sticky='W')
        global_controls_section = tk.Label(frame, text='Global Controls')
        global_controls_section.pack()

        tk.Button(
            frame,
            text='\u25B6',
            command=lambda: self._push_event_to_sequencer(SequencerEvent('play_or_stop')),
        ).pack(side=tk.LEFT)

        tk.Scale(
            frame,
            from_=MIN_BPM,
            to=MAX_BPM,
            command=lambda bpm: self._push_event_to_sequencer(SequencerEvent('set_bpm', {'bpm': bpm})),
            label='Beats per minute',
            orient=tk.HORIZONTAL,
            length=GLOBAL_SLIDER_WIDTH,
        ).pack(side=tk.LEFT)

        tk.Scale(
            frame,
            from_=MIN_PULSES_PER_BEAT,
            to=MAX_PULSES_PER_BEAT,
            command=lambda ppm: self._push_event_to_sequencer(SequencerEvent('set_ppm', {'ppm': ppm})),
            label='Pulses per beat',
            orient=tk.HORIZONTAL,
            length=GLOBAL_SLIDER_WIDTH,
        ).pack(side=tk.LEFT)

    def _get_drum_controls(self):
        frame = tk.Frame(
            self.frame,
            highlightbackground="green",
            highlightcolor="green",
            highlightthickness=1,
            width=500,
            height=100,
            bd=0,
        )
        frame.grid(column=0, row=0)
        tk.Label(frame, text='Drum Controls').pack(side=tk.TOP)
        for drum in range(3):
            tk.Label(frame, text=f'Drum {drum}').pack(side=tk.TOP)

    def _get_sequencer_grid(self):
        frame = tk.Frame(
            self.frame,
            highlightbackground="green",
            highlightcolor="green",
            highlightthickness=1,
            width=500,
            height=100,
            bd=0,
        )
        frame.grid(column=1, row=0)
        sequencer_grid = SequencerGrid(frame)
        tk.Label(frame, text='Sequencer Grid').pack()
        return sequencer_grid


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


class SequencerGrid:
    """
    Attributes
        lanes

    Methods
        draw
    """
    def __init__(self, parent):
        HEIGHT = 200
        WIDTH = 400

        n_drums = 3
        lane_height = int(HEIGHT / n_drums)

        self.n_cells = 16

        self.height = HEIGHT
        self.width = WIDTH
        self.canvas = tk.Canvas(parent, bg=GRID_BACKGROUND_COLOUR, height=self.height, width=self.width)
        self.canvas.bind('<Button-1>', self.on_click)

        self.lanes = list(reversed([
            SequencerLane(
                height=lane_height,
                top=(lane_height * i),
                grid=self,
                _id=i,
            ) for i in range(n_drums)
        ]))

        self.current_step = 0

        self.current_step_marker = self.canvas.create_rectangle(
            *self._get_current_step_marker_coords(),
            outline=CURRENT_STEP_MARKER_COLOUR,
            width=5,
        )

        self.canvas.pack()

    def on_click(self, event):
        for lane in self.lanes:
            if event.y > lane.top:
                return lane.on_click(event)

    def _get_current_step_marker_coords(self):
        cell_width = int(self.width / self.n_cells)
        return [
            self.current_step * cell_width,
            0,
            (self.current_step + 1) * cell_width,
            self.height,
        ]


class SequencerLane:
    """
    Attributes:
        cells

    Methods:
        draw

    """

    MARGIN = 1
    COLOUR = LANE_COLOUR

    def __init__(self, height, top, grid, _id):

        self.height = height
        self.top = top
        self.grid = grid
        self._id = _id

        self.coords = [
            self.MARGIN,
            top + self.MARGIN,
            grid.width - self.MARGIN,
            top + height - self.MARGIN,
        ]

        self.grid.canvas.create_rectangle(
            *self.coords,
            fill=self.COLOUR,
        )

        cell_width = int(self.grid.width / self.grid.n_cells)

        self.cells = list(reversed([
            SequencerCell(
                width=cell_width,
                top=top,
                right=(i * cell_width),
                lane=self,
                height=height,
                _id=i,
            ) for i in range(self.grid.n_cells)
        ]))

        for cell in self.cells:
            cell.draw()

    def on_click(self, event):
        for cell in self.cells:
            if event.x > cell.right:
                return cell.on_click()


class SequencerCell:
    """
    Attributes:
        is_on
        is_current

    Methods:
        draw
        toggle
    """

    MARGIN = 1
    COLOURS = {'OFF': CELL_OFF_COLOUR, 'ON': CELL_ON_COLOUR, 'BORDER': CELL_BORDER_COLOUR }

    def __init__(self, width, top, height, right, lane, _id):
        self.width = width
        self.top = top
        self.height = height
        self.right = right
        self.lane = lane
        self._id = _id
        self.is_on = False

        self.coords = [
            right + self.MARGIN,
            top + self.MARGIN,
            right + width - self.MARGIN,
            top + height - self.MARGIN,
        ]

        self.rectangle = self.lane.grid.canvas.create_rectangle(*self.coords, fill=self.COLOURS['OFF'], outline=self.COLOURS['BORDER'])

    def toggle(self):
        self.is_on = not self.is_on

    def draw(self):
        self.lane.grid.canvas.itemconfig(self.rectangle, fill=self.COLOURS['ON' if self.is_on else 'OFF'])

    def on_click(self):
        self.toggle()
        self.draw()

if __name__ == '__main__':
    sequencer_gui_interface = SequencerGUIInterface()
    GUI(sequencer_gui_interface=sequencer_gui_interface)

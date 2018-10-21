import math
import time
import cairo

from gi.repository import Gtk, GLib


# studio clock that displays a clock like mentioned in:
# https://masterbase.at/studioclock/#C3CD2D
class StudioClock(Gtk.ToolItem):
    __gtype_name__ = 'StudioClock'

    # set resolution of the update timer in seconds
    timer_resolution = 0.5
    last_draw_time = time.localtime(0)

    # init widget
    def __init__(self):
        super().__init__()
        # suggest size of widget
        self.set_size_request(130, 50)
        # remember last draw time
        self.last_draw_time = time.time()
        # set up timeout for periodic redraw
        GLib.timeout_add(self.timer_resolution * 1000, self.do_timeout)

    def do_timeout(self):
        # get current time
        current_time = time.time()
        # if time did not change since last redraw
        if current_time - self.last_draw_time >= 1.0:
            self.last_draw_time = current_time
            self.queue_draw()
        # just come back
        return True

    # override drawing of the widget
    def do_draw(self, cr):
        context = self.get_style_context()

        flags = Gtk.StateFlags.NORMAL
        color_normal = context.get_color(flags)
        border_color_normal = context.get_border_color(flags)
        background_color_normal = context.get_background_color(flags)
        font_normal = context.get_font(flags).get_family()

        flags = Gtk.StateFlags.SELECTED
        color_selected = context.get_color(flags)
        border_color_selected = context.get_border_color(flags)
        background_color_selected = context.get_background_color(flags)

        #rgba_on = tuple(background_color_selected)
        #rgba_off = tuple(color_normal)

        rgba_on = tuple(color_normal)
        rgba_off = tuple(background_color_normal)

        # get actual widget size
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        # calculate center and radius of the clock
        center = (width / 2, height / 2)
        radius = min(center)
        local_time = time.localtime(self.last_draw_time)
        # draw ticks for every second
        for tick in range(0, 60):
            # fade out seconds in future and highlight past seconds
            if tick <= local_time.tm_sec:
                cr.set_source_rgba(*rgba_on)
            elif rgba_off:
                cr.set_source_rgba(*rgba_off)

            # calculate tick position
            angle = tick * math.pi / 30
            pos = (center[0] + math.sin(angle) * radius * 0.8,
                   center[1] - math.cos(angle) * radius * 0.8)
            # draw tick
            cr.arc(pos[0], pos[1], radius / 40, 0, 2 * math.pi)
            cr.fill()
        # draw persistant ticks every five seconds
        cr.set_source_rgba(*rgba_on)
        for tick in range(0, 12):
            # calculate tick position
            angle = tick * math.pi / 6
            pos = (center[0] + math.sin(angle) * radius * 0.9,
                   center[1] - math.cos(angle) * radius * 0.9)
            # draw tick
            cr.arc(pos[0], pos[1], radius / 40, 0, 2 * math.pi)
            cr.fill()
        # set a reasonable font size
        cr.set_font_size(cr.user_to_device_distance(0, height / 5)[1])
        cr.select_font_face(font_normal, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        # format time into a string
        text = "{:02d}:{:02d}".format(local_time.tm_hour, local_time.tm_min)
        # get text drawing extents
        (xbearing, ybearing,
         textwidth, textheight,
         xadvance, yadvance) = cr.text_extents(text)
        # draw time
        cr.move_to(center[0] - textwidth / 2, center[1] + textheight / 2)
        cr.show_text(text)

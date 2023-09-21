import numpy as np
import scipy.interpolate as interpolate
import matplotlib.pyplot as plt
import os

def make_spline(
    via_x, via_y, via_speed=None, speed_accel_parameter=0.2, speed_decay_parameter=0.8, 
    total_time_length=5, num_timesteps=200, num_delta_t=200000, s=0, **kwargs):
    print(speed_accel_parameter)
    window_size = int(num_delta_t / num_timesteps)
    accel_time = total_time_length * speed_accel_parameter
    decay_time = total_time_length * speed_decay_parameter
    dt = total_time_length/num_delta_t
    tck, u = interpolate.splprep([via_x, via_y], s=s)
    xi, yi = interpolate.splev(np.linspace(0, 1, num_delta_t + 1), tck)
    dxi = xi[1:] - xi[:-1]
    dyi = yi[1:] - yi[:-1]
    total_length = np.sum(np.sqrt(dxi**2 + dyi**2))
    eps = 1e-6

    if via_speed is not None:
        if type(via_speed) is list:
            via_speed = np.array(via_speed, dtype=float)
        tck_speed, u = interpolate.splprep(
            [via_speed], u=np.linspace(accel_time, decay_time, via_speed.shape[0]), s=s)
        def get_speed_before_normalized(t):
            if type(t) == np.ndarray:
                speed = np.zeros(t.shape)
                c0 = via_speed[0]/((accel_time)**2 + eps)
                speed[t<=accel_time] = -c0*((t[t<=accel_time]-accel_time)**2)+via_speed[0]
                speed[(t<=decay_time)*(t>accel_time)] = interpolate.splev(t[(t<=decay_time)*(t>accel_time)], tck_speed)[0]
                c1 = via_speed[-1]/((total_time_length-decay_time)**2 + eps)
                speed[t>decay_time] = -c1*((t[t>decay_time]-decay_time)**2)+via_speed[-1]
            return speed
    else:
        def get_speed_before_normalized(t):
            if type(t) == np.ndarray:
                speed = np.ones(t.shape)
                c0 = 1/((accel_time)**2 + eps)
                speed[t<=accel_time] = -c0 * ((t[t<=accel_time]-accel_time)**2) + 1
                c1 = 1 / ((total_time_length-decay_time)**2 + eps)
                speed[t>decay_time] = -c1 * ((t[t>decay_time]-decay_time)**2) + 1
            return speed

    speed_array_temp = get_speed_before_normalized(
        np.linspace(0, total_time_length, num_delta_t + 1))
    speed_int_temp = np.sum((speed_array_temp[:-1] + speed_array_temp[1:])/2 * dt)
    speed_mult_coeff = total_length / speed_int_temp
    speed_array = speed_mult_coeff * speed_array_temp
    delta_l = np.zeros(num_timesteps)

    for k in range(num_timesteps):
        delta_l[k] = np.sum(
            (speed_array[k*window_size: (k+1)*window_size] + 
            speed_array[k*window_size + 1: (k+1)*window_size + 1])/2 * dt)

    xy_final = np.zeros([num_timesteps + 1, 2])
    dxydt_final = np.zeros([num_timesteps + 1, 2])

    def cal_step(i):
        dx = dxi[i]
        dy = dyi[i]
        dl_step = np.sqrt(dx**2 + dy**2, dtype=np.float32)
        return dl_step
    k = 0
    target_l = 0
    current_l = 0
    for i in range(xi.shape[0]-1):
        if current_l >= target_l:
            xy_final[k, 0] = xi[i]
            xy_final[k, 1] = yi[i]
            dxydt_final[k, 0] = dxi[i] * (speed_array[i] / (np.sqrt(dxi[i]**2 + dyi[i]**2)))
            dxydt_final[k, 1] = dyi[i] * (speed_array[i] / (np.sqrt(dxi[i]**2 + dyi[i]**2)))
            target_l += delta_l[k]
            k += 1
        current_l += cal_step(i)
        if k == num_timesteps:
            break
    xy_final[-1, 0] = xi[-1]
    xy_final[-1, 1] = yi[-1]
    dxydt_final[-1, 0] = dxi[-1] * (speed_array[-1] / (np.sqrt(dxi[-1]**2 + dyi[-1]**2)))
    dxydt_final[-1, 1] = dyi[-1] * (speed_array[-1] / (np.sqrt(dxi[-1]**2 + dyi[-1]**2)))
    return xy_final, dxydt_final

class SplineMaker:
    def __init__(self, start_point_pos=None, final_point_pos=None, 
    xlim=[-1, 6], ylim=[-1, 6], title='noname', save_path='./saved/', **kwargs):
        """
        Spline maker.
        1. Run the script
        1. Click desired via points
        2. Type 'v' on the keyboard for spline making.
        3. Type 'c' on the keypoard for saving.
        
        A1. You can undo your last click by typing 'z'
        A2. Default ordering option is click order. There is another option, ascending order in x axis.
            If you want to switch between them, type 'b' on the keyboard
        A3. Type 'r' for reset.
        """
        self.kwargs = kwargs
        self.xlim = xlim 
        self.ylim = ylim 
        self.start_point_pos = start_point_pos
        self.final_point_pos = final_point_pos
        self.xs = []
        self.ys = []
        # self.press = False
        self.order = 'time_ascending'
        self.title = title
        self.save_path = save_path
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        if self.start_point_pos is None:
            self.click_level = 0
        else:
            self.click_level = 3
        self.init_figure()

    def init_figure(self):
        if hasattr(self, 'reddots'):
            del self.reddots
        if hasattr(self, 'fig'):
            plt.close('all')
            del self.fig, self.ax
        self.fig = plt.figure(figsize=[8, 8])

        self.fig.canvas.mpl_connect('key_press_event', self.key_press)
        self.fig.canvas.mpl_connect('button_press_event', self.click)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("v:spline, c:save, r:reset, z:undo, b:switch_ordering")
        self.ax.set_xlim(self.xlim[0], self.xlim[1])
        self.ax.set_ylim(self.ylim[0], self.ylim[1])
        self.ax.grid(zorder=0)
        self.ax.xaxis.set_major_locator(plt.MultipleLocator(1))
        self.ax.xaxis.set_minor_locator(plt.MultipleLocator(0.1))
        self.ax.yaxis.set_major_locator(plt.MultipleLocator(1))
        self.ax.yaxis.set_minor_locator(plt.MultipleLocator(0.1))
        if self.start_point_pos is not None:
            self.start_point = self.ax.plot(
                [self.start_point_pos[0]], [self.start_point_pos[1]], 'go', markersize=18, zorder=2)
        if self.final_point_pos is not None:
            if self.final_point_pos[0] != self.start_point_pos[0] or self.final_point_pos[1] != self.start_point_pos[1]:
                self.final_point = self.ax.plot(
                    [self.final_point_pos[0]], [self.final_point_pos[1]], 'bs', markersize=18, zorder=2)
        plt.show()

    def reset_figure(self):
        self.xs = []
        self.ys = []
        if hasattr(self, 'reddots'):
            line = self.reddots
            line.remove()
            del self.reddots
        if hasattr(self, 'spline'):
            line = self.spline.pop(0)
            line.remove()
            del self.spline
        if hasattr(self, 'spline_dots'):
            line = self.spline_dots.pop()
            line.remove()
            del self.spline_dots

        if self.click_level == 3:
            pass
        else:
            self.final_point_pos = None
            self.start_point_pos = None
            self.click_level = 0
            if hasattr(self, 'start_point'):
                line = self.start_point.pop(0)
                line.remove()
                del self.start_point
            if hasattr(self, 'final_point'):
                line = self.final_point.pop(0)
                line.remove()
                del self.final_point
        self.fig.canvas.draw()


    def key_press(self,event):
        # Try to avoid using preassigned shortcuts: 'q'; quit, 's'; save, 'o'; zoom, and 'f'; fullscreen.
        
        print('key_press', event.key)
        if event.key == 'v':  # make spline
            print("Spline making..")
            if hasattr(self, 'spline'):
                line = self.spline.pop(0)
                line.remove()
                del self.spline
            if hasattr(self, 'spline_dots'):
                line = self.spline_dots.pop()
                line.remove()
                del self.spline_dots
            self.make_spline()
        
        if event.key == 'c':  # save spline
            print("Spline saving..")
            if hasattr(self, 'xy_final'):
                self.make_path()
                with open(self.total_path, 'wb') as f:
                    np.save(f, (self.xy_final, self.dxydt_final))
            else:
                if hasattr(self, 'spline'):
                    line = self.spline.pop(0)
                    line.remove()
                    del self.spline
                if hasattr(self, 'spline_dots'):
                    line = self.spline_dots.pop()
                    line.remove()
                    del self.spline_dots
                self.make_spline()

        if event.key == 'z':  # undo
            if len(self.xs) > 0:
                del self.xs[-1]
                del self.ys[-1]
            self.reddots.set_data(self.xs, self.ys)
            self.fig.canvas.draw()

        if event.key == 'b':  # switch order
            if self.order == 'time_ascending':
                print('Switching order from time_ascending to x_ascending.')
                self.order = 'x_ascending'
            elif self.order == 'x_ascending':
                print('Switching order from x_ascending to time_ascending.')
                self.order = 'time_ascending'

        if event.key == 'r':  # reset
            self.reset_figure()
            pass
        
    def click(self, event):
        print('click', event)
        if event.inaxes!=self.ax: return
        else:
            if self.click_level == 0:
                self.start_point_pos = [event.xdata, event.ydata]
                self.start_point = self.ax.plot(
                    [self.start_point_pos[0]], [self.start_point_pos[1]], 'go', markersize=18, zorder=2)
                self.click_level = 1
            elif self.click_level == 1:
                self.final_point_pos = [event.xdata, event.ydata]
                self.final_point = self.ax.plot(
                    [self.final_point_pos[0]], [self.final_point_pos[1]], 'bs', markersize=18, zorder=2)
                self.click_level = 2
            elif self.click_level >= 2:
                if not hasattr(self, 'reddots'):
                    self.reddots, = self.ax.plot([event.xdata], [event.ydata], 'ro', zorder=3)  # empty line
                self.xs.append(event.xdata)
                self.ys.append(event.ydata)
                self.reddots.set_data(self.xs, self.ys)
            self.fig.canvas.draw()

    def make_path(self):
        if not hasattr(self, 'total_path'):
            self.total_path = self.save_path+self.title+'.npy'
        if not hasattr(self, 'current_num'):
            self.current_num = 0

        if os.path.exists(self.total_path):
            while os.path.exists(self.total_path):
                self.current_num += 1
                self.total_path = self.save_path+self.title+'_'+str(self.current_num)+'.npy'

    def make_spline(self, save=False):
        if self.order == 'time_ascending':
            via_x = np.array(self.xs)
            via_y = np.array(self.ys)
        elif self.order == 'x_ascending':
            via_x = np.array(self.xs)
            index = np.argsort(via_x)
            via_x = via_x[index]
            via_y = np.array(self.ys)[index]
        
        via_x = np.concatenate(
            (np.array([self.start_point_pos[0]], dtype=float), via_x, 
            np.array([self.final_point_pos[0]], dtype=float)), axis=0)
        via_y = np.concatenate(
            (np.array([self.start_point_pos[1]], dtype=float), via_y, 
            np.array([self.final_point_pos[1]], dtype=float)), axis=0)
        self.xy_final, self.dxydt_final = make_spline(via_x, via_y, **self.kwargs)
        self.spline = self.ax.plot(self.xy_final[:, 0], self.xy_final[:, 1], color='tab:blue', linewidth=2, zorder=1)
        len_traj = len(self.xy_final)
        self.spline_dots = self.ax.plot(self.xy_final[::int(len_traj/30), 0], self.xy_final[::int(len_traj/30), 1], 'o', color='tab:purple', markersize=3, zorder=4)
        self.fig.canvas.draw()
        if save == True:
            self.make_path()
            with open(self.total_path, 'wb') as f:
                np.save(f, (self.xy_final, self.dxydt_final))
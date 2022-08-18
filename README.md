# Easy-2D-spline-maker-python
Easily design your own 2D spline with custom speed profile by just a few clicks!
The number of via points are free.

## Requirements
The tool requires following python packages:
- numpy
- scipy
- matplotlib
- PyYAML

## Running examples

### 1. Fully click based
You can set the start_point_pos and final_point_pos points by clicks.
```js
python run.py --config configs/click_based.yaml
```

### 2. Initial & final points specified
You may also prespecify start_point_pos and final_point_pos.
```js
python run.py --config configs/init_fin_specified.yaml
```

### 3. Periodic trajectory
If you set start_point_pos and final_point_pos the same, the spline trajectory will be periodic.
For periodic trajectory, speed_accel_parameter: 0, and speed_decay_parameter: 1 are highly recommended.
```js
python run.py --config configs/periodic.yaml
```

### 4. Custom speed profile 
```js
python run.py --config configs/custom_speed.yaml
```

## yaml explanation
* title: 'Spline_test' - <b>The title of the run.</b>
* save_path: './saved/' - <b>The save path.</b>
* xlim: [-1, 6]  - <b>xlim of figure.</b>
* ylim: [-1, 6]  - <b>ylim of figure.</b>
* start_point_pos: [0, 0]  - <b>The start point of the spline (optional).</b>
* final_point_pos: [5, 0]  - <b>The final point of the spline (optional).</b>
* via_speed: [1.0, 2.0, 3.0, 3.0, 3.0]  - <b>Via points of your custom speed profile (optional). </b>
* speed_accel_parameter: 0.2  - <b>The ratio of timesteps until which the trajectory accelerates to the speed from 0 to the initial speed of your speed profile. Set 0 if you don't want it.</b>
* speed_decay_parameter: 0.8  - <b>The ratio of timesteps from which the trajectory decelerates to the speed from the final speed of your speed profile to 0. Set 1 if you don't want it.</b>
* total_time_length: 5  - <b>Total time length of the trajectory. Speed profile is normalized to satisfy total_time_length. </b>
* num_timesteps: 200  - <b>The number of timesteps of your spline.</b>
* num_delta_t: 200_000  - <b>The number of timesteps for numerical integration & derivation.</b>
* s: 0  - <b>The smoothing factor for 'scipy.integrate'. if s is larger than 0, the spline will be smoother but might not go through the via points. </b>
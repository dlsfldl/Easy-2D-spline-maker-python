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
* title: 'Spline_test' - The title of the run.
* save_path: './saved/' - The save path.
* xlim: [-1, 6]  - xlim of figure.
* ylim: [-1, 6]  - ylim of figure.
* start_point_pos: [0, 0]  - The start point of the spline (optional).
* final_point_pos: [5, 0]  - The final point of the spline (optional).
* via_speed: [1.0, 2.0, 3.0, 3.0, 3.0]  - Via points of your custom speed profile (optional). 
* speed_accel_parameter: 0.2  - The ratio of timesteps until which the trajectory accelerates to the speed from 0 to the initial speed of your speed profile. Set 0 if you don't want it.
* speed_decay_parameter: 0.8  - The ratio of timesteps from which the trajectory decelerates to the speed from the final speed of your speed profile to 0. Set 1 if you don't want it.
* total_time_length: 5  - Total time length of the trajectory. Speed profile is normalized to satisfy total_time_length. 
* num_timesteps: 200  - The number of timesteps of your spline.
* num_delta_t: 200_000  - The number of timesteps for numerical integration & derivation.
* s: 0  - The smoothing factor for 'scipy.integrate'. if s is larger than 0, the spline will be smoother but might not go through the via points. 
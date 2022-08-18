import yaml
import argparse
from module.spline import SplineMaker


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str)
    args, unknown = parser.parse_known_args()
    dict = yaml.load(open(args.config), Loader=yaml.FullLoader)
    print('Configuration:')
    print(dict)

    model = SplineMaker(**dict)

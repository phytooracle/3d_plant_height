#!/usr/bin/env python3
"""
Author : Emmanuel Gonzalez
Date   : 2021-04-26
Purpose: Plant height extraction
"""

import argparse
import os
import sys
import glob
import open3d as o3d
import pandas as pd
import multiprocessing

# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Plant height extraction',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('dir',
                        metavar='dir',
                        type=str,
                        help='Directory containing individual plant pointclouds')

    parser.add_argument('-od',
                        '--outdir',
                        help='Output directory',
                        metavar='str',
                        type=str,
                        default='3d_plant_height')

    parser.add_argument('-of',
                        '--outfile',
                        help='Outfile path',
                        metavar='str',
                        type=str,
                        default='plant_height')

    return parser.parse_args()


# --------------------------------------------------
def process_pointcloud(pcd_path):
    height_list = []
    plant_name_list = []
    dir_name_list = []
    vol_list = []

    df = pd.DataFrame()

    plant_name = os.path.splitext(os.path.basename(pcd_path))[0]
    plant_name = '_'.join(plant_name.split('_')[:-1])
    plant_name_list.append(plant_name)
    print(f'Processing {plant_name}.')

    dir_name = os.path.split(os.path.dirname(pcd_path))[-1]
    dir_name_list.append(dir_name)

    pcd = o3d.io.read_point_cloud(pcd_path)
    box = o3d.geometry.AxisAlignedBoundingBox.create_from_points(pcd.points)
    vol = box.volume()
    vol_list.append(vol)

    height_list.append(abs(float(pcd.get_max_bound()[2]) - float(pcd.get_min_bound()[2])))

    df['height_meters'] = height_list
    df['volume_meters_3'] = vol_list
    df['plant_name'] = plant_name_list
    df['origin_directory'] = dir_name_list
    return df


# --------------------------------------------------
def main():
    """Make a jazz noise here"""

    args = get_args()
    
    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)
    
    major_df = pd.DataFrame()

    with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
        df = p.map(process_pointcloud, glob.glob(os.path.join(args.dir)))
        major_df = major_df.append(df)

    major_df.to_csv(os.path.join(args.outdir, f'{args.outfile}.csv'), index=False)

    print(f'Done, see outputs in ./{args.outdir}.')



# --------------------------------------------------
if __name__ == '__main__':
    main()

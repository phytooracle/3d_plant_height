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
def get_paths(directory):
    pcd_list = []

    for root, dirs, files in os.walk(directory):
        for name in files:
            if '.ply' in name:
                pcd_list.append(os.path.join(root, name))

    if not pcd_list:

        raise Exception(f'ERROR: No compatible images found in {directory}.')


    print(f'Point clouds to process: {len(pcd_list)}')

    return pcd_list


# --------------------------------------------------
def process_pointcloud(pcd_path):
    try:
        
        height_list = []
        plant_name_list = []
        dir_name_list = []
        axis_vol_list = []
        oriented_vol_list = []

        df = pd.DataFrame()

        plant_name = os.path.splitext(os.path.basename(pcd_path))[0]
        plant_name = '_'.join(plant_name.split('_')[:-1])
        plant_name_list.append(plant_name)
        print(f'Processing {plant_name}.')

        dir_name = os.path.split(os.path.dirname(pcd_path))[-1]
        dir_name_list.append(dir_name)

        pcd = o3d.io.read_point_cloud(pcd_path)
        axis_aligned_box = o3d.geometry.AxisAlignedBoundingBox.create_from_points(pcd.points)
        oriented_box = o3d.geometry.OrientedBoundingBox.create_from_points(pcd.points)

        axis_vol = axis_aligned_box.volume()
        axis_vol_list.append(axis_vol)

        oriented_vol = oriented_box.volume()
        oriented_vol_list.append(oriented_vol)

        height_list.append(abs(float(pcd.get_max_bound()[2]) - float(pcd.get_min_bound()[2])))

        df['height_meters'] = height_list
        df['axis_aligned_volume'] = axis_vol_list
        df['oriented_volume'] = oriented_vol_list
        df['plant_name'] = plant_name_list
        df['origin_directory'] = dir_name_list

    except:
        pass
    
    return df


# --------------------------------------------------
def main():
    """Make a jazz noise here"""

    args = get_args()
    
    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)
    
    major_df = pd.DataFrame()
    paths = get_paths(args.dir)

    with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
        df = p.map(process_pointcloud, paths)
        major_df = major_df.append(df)

    major_df.to_csv(os.path.join(args.outdir, f'{args.outfile}.csv'), index=False)

    print(f'Done, see outputs in ./{args.outdir}.')



# --------------------------------------------------
if __name__ == '__main__':
    main()

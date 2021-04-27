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
    df = pd.DataFrame()

    plant_name = os.path.splitext(os.path.basename(pcd_path))[0]
    plant_name_list.append(plant_name)

    pcd = o3d.io.read_point_cloud(pcd_path)
    height_list.append(abs(float(pcd.get_max_bound()[2]) - float(pcd.get_min_bound()[2])))

    df['height_meters'] = height_list
    df['plant_name'] = plant_name_list
    
    return df


# --------------------------------------------------
def main():
    """Make a jazz noise here"""

    args = get_args()
    
    if not os.path.isdir(args.outdir):
        os.makedirs(args.outdir)
    
    major_df = pd.DataFrame()

    with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
        df = p.map(process_pointcloud, glob.glob(os.path.join(args.dir, '*.ply')))
        major_df = major_df.append(df)

    major_df.to_csv(os.path.join(args.outdir, f'{args.outfile}.csv'), index=False)

    print(f'Done, see outputs in ./{args.outdir}.')



# --------------------------------------------------
if __name__ == '__main__':
    main()

from math import pi
from operator import index
import os
import pickle
import argparse
import json
import numpy as np
import pandas as pd
import subprocess
import gzip
import logging

def examine_inter_pae(pae_mtx, seqs, cutoff):
    """A function that checks inter-pae values in multimer prediction jobs"""
    lens = [len(seq) for seq in seqs]
    old_lenth = 0
    for length in lens:
        new_length = old_lenth + length
        pae_mtx[old_lenth:new_length, old_lenth:new_length] = 50
        old_lenth = new_length
    check = np.where(pae_mtx < cutoff)[0].size != 0

    return check

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", type = str, help="path to the output directory")
    parser.add_argument("--cutoff", type=float, default=100.0, help="cutoff of PAE values. By default 100")
    args = parser.parse_args()
    jobs = os.listdir(args.output_dir)
    good_jobs = []
    iptm_ptm = []
    iptm = []
    count = 0
    for job in jobs:
        logging.info(f"now processing {job}")
        count = count + 1
        if os.path.isfile(os.path.join(args.output_dir, job, "ranking_debug.json")):
            result_subdir = os.path.join(args.output_dir, job)
            best_result = json.load(open(os.path.join(args.output_dir, job, "ranking_debug.json")))['order'][0]
            best_result = "result_" + best_result
            if os.path.exists(os.path.join(result_subdir, best_result+'.pkl')) and not os.path.exists(os.path.join(result_subdir, best_result + ".pkl.gz")):
                result_path = os.path.join(result_subdir, best_result+'.pkl')
                check_dict = pickle.load(open(result_path, "rb"))
                seqs = pickle.load(open(result_path, "rb"))["seqs"]
                
            elif not os.path.exists(os.path.join(result_subdir, best_result)) and os.path.exists(os.path.join(result_subdir, best_result + ".pkl.gz")):
                result_path = os.path.join(result_subdir, best_result+".pkl.gz")
                check_dict = pickle.load(gzip.open(result_path, "rb"))
                seqs = pickle.load(gzip.open(result_path, "rb"))["seqs"]
            elif not os.path.exists(os.path.join(result_subdir, best_result+'.pkl')) and not os.path.exists(os.path.join(result_subdir, best_result + ".pkl.gz")):
                raise FileNotFoundError(f"Neither result.pkl nor result.pkl.gz is found for {os.path.join(result_subdir,best_result)}. Please check if the directory is corrupted")
            else:
                result_path = os.path.join(result_subdir, best_result+'.pkl')
                check_dict = pickle.load(open(result_path, "rb"))
                seqs = pickle.load(open(result_path, "rb"))["seqs"]    
            
            best_model = json.load(
                open(os.path.join(result_subdir, "ranking_debug.json"), "rb")
            )["order"][0]

            # below first check whether it is a job in monomer mode or multimer
            data = json.load(
                open(os.path.join(result_subdir, "ranking_debug.json"), "rb")
            )

            if "iptm" in data.keys() or "iptm+ptm" in data.keys():
                iptm_ptm_score = data["iptm+ptm"][best_model]
                iptm_score = check_dict["iptm"]
                pae_mtx = check_dict["predicted_aligned_error"]
                check = examine_inter_pae(pae_mtx, seqs, cutoff=args.cutoff)
                if check:
                    good_jobs.append(str(job))
                    iptm_ptm.append(iptm_ptm_score)
                    iptm.append(iptm_score)
        logging.info(f"done for {job} {count} out of {len(jobs)} finished.")

    pi_score_df = pd.DataFrame()
    pi_score_df["jobs"] = good_jobs
    pi_score_df["iptm+ptm"] = iptm_ptm
    pi_score_df["iptm"] = iptm

    pi_score_df = pi_score_df.sort_values(by="iptm", ascending=False)

if __name__ == "__main__":
    main()
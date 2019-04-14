#!/usr/bin/env python3

import sys
import subprocess
import csv
from collections import defaultdict
import shutil
import os
import time
from config import Config
from pcfg_mower import pcfg_mower

if sys.version_info[0] < 3:
    print("This program requires Python 3.x", file=sys.stderr)
    sys.exit(1)

#grammar_dir = "/home/pcfg/oldserver/pcfg/go/Rules/"
#pcfg_mower_dir = "/home/pcfg/oldserver/pcfg/pcfg_mower/"
#go_manager_dir = "/home/pcfg/oldserver/pcfg/go/"


grammar_dir = "/home/ef/DP/pcfg_mower/Rules/"
pcfg_mower_dir = "/home/ef/DP/pcfg_mower/"
go_manager_dir = "/home/ef/go/src/pcfg-manager/"
dictmatcher_bin = "/home/ef/DP/fitcrack-utils/dictmatcher/bin/dictmatcher"
grammar_input_arr = ['DP700']
cracking_ref_arr = ['/home/ef/DP/SecLists/Passwords/Leaked-Databases/rockyou-65.txt',
                    '/home/ef/DP/SecLists/Passwords/probable-v2-top12000.txt',
                    '/home/ef/DP/SecLists/Passwords/edited/myspace.txt',
                    '/home/ef/DP/SecLists/Passwords/edited/darkweb2017-10000_removed_long.txt']
mower_settings = dict()
output_dir = ""

res = defaultdict(dict)

red = lambda text: '\033[0;31m' + text + '\033[0m'
green = lambda text: '\033[0;32m' + text + '\033[0m'


def get_grammar_stats(grammar):
    path = grammar_dir + grammar
    res[grammar]["Alpha_size"] = subprocess.getoutput("wc -l " + path + "/Alpha/* | tail -n 1").split()[0]
    res[grammar]["Grammar_size"] = subprocess.getoutput("wc -l " + path + "/Grammar/Grammar.txt | tail -n 1").split()[0]
    res[grammar]["Grammar_prob"] = subprocess.getoutput("cat " + path + "/Grammar/Grammar.txt | cut -f 2 | awk '{s+=$1} END {print s}'")
    res[grammar]["Cap_size"] = subprocess.getoutput("wc -l " + path + "/Capitalization/* | tail -n 1").split()[0]
    res[grammar]["Cap_prob"] = subprocess.getoutput("cat " + path + "/Capitalization/* | cut -f 2 | awk '{s+=$1} END {print s}'")


def main():
     # INPUT
     #  - Grammars
     #  - path to scripts
     #  - mower settings
     #  - aa settings
     #  - output

    for grammar_name in grammar_input_arr:
        get_grammar_stats(grammar_name)

        ########################################################################################################
        # REMOVE LONG BASE
        path_to_rlb_grammar = grammar_dir + grammar_name + "_rlb/"
        out = subprocess.getoutput("cp -r " + grammar_dir + grammar_name + " " + path_to_rlb_grammar)
        print(out)
        out = subprocess.getoutput("./remove_long_base.sh " + path_to_rlb_grammar + "Grammar/Grammar.txt")
        print(out)
        get_grammar_stats(grammar_name + "_rlb")

        ########################################################################################################
        # RUN PCFG_MOWER
        # mow1000M
        path_to_mow1000M_grammar = grammar_dir + grammar_name + "_mow1000M/"
        config = Config

        config.input_dir = path_to_rlb_grammar
        config.output_dir = path_to_mow1000M_grammar
        config.limit = 5000000

        pcfg_mower(config)

        get_grammar_stats(grammar_name + "_mow1000M")

        ########################################################################################################
        # RUN PCFG_MOWER
        # mow500M
        path_to_mow500M_grammar = grammar_dir + grammar_name + "_mow500M/"
        config.output_dir = path_to_mow500M_grammar
        config.limit = 3000000

        pcfg_mower(config)

        get_grammar_stats(grammar_name + "_mow500M")

        ########################################################################################################
        # RUN PCFG_MOWER
        # aa1000M
        path_to_aa1000M_grammar = grammar_dir + grammar_name + "_aa1000M/"
        config.output_dir = path_to_aa1000M_grammar
        config.limit = 5000000
        config.attack_dict_file = "attack_dict_config"

        pcfg_mower(config)

        get_grammar_stats(grammar_name + "_aa1000M")

        ########################################################################################################
        # RUN PCFG_MOWER
        # aa500M
        path_to_aa500M_grammar = grammar_dir + grammar_name + "_aa500M/"
        config.output_dir = path_to_aa500M_grammar
        config.limit = 3000000
        config.attack_dict_file = "attack_dict_config"

        pcfg_mower(config)

        get_grammar_stats(grammar_name + "_aa500M")

        ########################################################################################################
        # RUN GO MANAGER
        output_guesses_grammar_dir = "output_guesses/" + grammar_name + "/"
        if os.path.isdir(output_guesses_grammar_dir):
            shutil.rmtree(output_guesses_grammar_dir)
        os.mkdir(output_guesses_grammar_dir)

        #for gr in res:
        #    in_gr = grammar_dir + gr
        #    out_gr = go_manager_dir + "Rules/" + gr
        #    if os.path.isdir(out_gr):
        #        print("Removing " + out_gr)
        #        shutil.rmtree(out_gr)
        #    shutil.copytree(in_gr, out_gr)

        for gr in res:
            print("go-manager " + gr, end='\t')
            start = time.time()
            (exitcode, output) = subprocess.getstatusoutput(go_manager_dir + "pcfg-manager -r " + gr + " > " + output_guesses_grammar_dir + gr)
            elapsed = round((time.time() - start),1)
            if exitcode == 0:
                print(green("OK"))
                res[gr]["Time"] = elapsed
                res[gr]["Size"] = os.stat(output_guesses_grammar_dir + gr).st_size
                res[gr]["Count"] = subprocess.getoutput("wc -l " + output_guesses_grammar_dir + gr).split()[0]
            else:
                print(red("FAIL"))

        ########################################################################################################
        # RUN DICTMATCHER
        for gr in res:
            for ref in cracking_ref_arr:
                print("dictmatcher " + gr, end='\t')
                (exitcode, out) = subprocess.getstatusoutput(dictmatcher_bin + " -e " + output_guesses_grammar_dir + gr + " -d " + ref)
                print(exitcode)
                print(out)
                if exitcode == 0:
                    res[gr][ref] = out

        print(res)

        # CREATE FANCY TABLE
        # with open('testrun.csv', mode='w') as file:
        #    output_csv = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #    output_csv.writerow(res)
     #
     # GET HIGH


    return 0



if __name__ == "__main__":
    main()
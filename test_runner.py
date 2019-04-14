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

#grammar_dir = "/home/pcfg/oldserver/pcfg/pcfg_mower/Rules/"
#go_manager_dir = "/home/pcfg/oldserver/pcfg/go/"
#output_guesses_dir = "/home/pcfg/oldserver/pcfg/pcfg_mower/"
#dictmatcher_dir = "/home/pcfg/oldserver/pcfg/dictmatcher/bin/"
#grammar_input_arr = ['DP700']
#cracking_ref_arr = ['/home/pcfg/oldserver/pcfg/SecLists/Passwords/Leaked-Databases/rockyou-65.txt',
#                    '/home/pcfg/oldserver/pcfg/SecLists/Passwords/probable-v2-top12000.txt',
#                    '/home/pcfg/oldserver/pcfg/SecLists/Passwords/edited/myspace.txt',
#                    '/home/pcfg/oldserver/pcfg/SecLists/Passwords/edited/darkweb2017-top10000_removed_long_pass.txt']

res = defaultdict(dict)

red = lambda text: '\033[0;31m' + text + '\033[0m'
green = lambda text: '\033[0;32m' + text + '\033[0m'

grammar_dir = "/home/ef/DP/pcfg_mower/Rules/"
go_manager_dir = "/home/ef/go/src/pcfg-manager/"
output_guesses_dir = "/home/ef/DP/pcfg_mower/"
dictmatcher_dir = "/home/pcfg/oldserver/pcfg/dictmatcher/bin/"
grammar_input_arr = ['DP700', 'DP700_copy']
cracking_ref_arr = ['/home/ef/DP/SecLists/Passwords/Leaked-Databases/rockyou-65.txt',
                    '/home/ef/DP/pcfg/SecLists/Passwords/probable-v2-top12000.txt',
                    '/home/ef/DP/pcfg/SecLists/Passwords/edited/myspace.txt',
                    '/home/ef/DP/pcfg/SecLists/Passwords/edited/darkweb2017-top10000_removed_long_pass.txt']

def get_grammar_stats(group_grammar, postfix):
    grammar = group_grammar + postfix
    path = grammar_dir + grammar
    res[group_grammar][grammar]["Alpha_size"] = subprocess.getoutput("wc -l " + path + "/Alpha/* | tail -n 1").split()[0]
    res[group_grammar][grammar]["Grammar_size"] = subprocess.getoutput("wc -l " + path + "/Grammar/Grammar.txt | tail -n 1").split()[0]
    res[group_grammar][grammar]["Grammar_prob"] = subprocess.getoutput("cat " + path + "/Grammar/Grammar.txt | cut -f 2 | awk '{s+=$1} END {print s}'")
    res[group_grammar][grammar]["Cap_size"] = subprocess.getoutput("wc -l " + path + "/Capitalization/* | tail -n 1").split()[0]
    res[group_grammar][grammar]["Cap_prob"] = subprocess.getoutput("cat " + path + "/Capitalization/* | cut -f 2 | awk '{s+=$1} END {print s}'")


def main():
     # INPUT
     #  - Grammars
     #  - path to scripts
     #  - mower settings
     #  - aa settings
     #  - output

    for grammar_name in grammar_input_arr:
        res[grammar_name] = defaultdict(dict)
        get_grammar_stats(grammar_name, "")

        ########################################################################################################
        # REMOVE LONG BASE
        path_to_rlb_grammar = grammar_dir + grammar_name + "_rlb/"
        out = subprocess.getoutput("cp -r " + grammar_dir + grammar_name + " " + path_to_rlb_grammar)
        print(out)
        out = subprocess.getoutput("./remove_long_base.sh " + path_to_rlb_grammar + "Grammar/Grammar.txt")
        print(out)
        get_grammar_stats(grammar_name, "_rlb")

        ########################################################################################################
        # RUN PCFG_MOWER
        # mow1000M
        path_to_mow1000M_grammar = grammar_dir + grammar_name + "_mow1000M/"
        config = Config

        config.input_dir = path_to_rlb_grammar
        config.output_dir = path_to_mow1000M_grammar
        config.limit = 5000000

        pcfg_mower(config)

        get_grammar_stats(grammar_name, "_mow1000M")

        ########################################################################################################
        # RUN PCFG_MOWER
        # mow500M
        path_to_mow500M_grammar = grammar_dir + grammar_name + "_mow500M/"
        config.output_dir = path_to_mow500M_grammar
        config.limit = 3000000

        pcfg_mower(config)

        get_grammar_stats(grammar_name, "_mow500M")

        ########################################################################################################
        # RUN PCFG_MOWER
        # aa1000M
        path_to_aa1000M_grammar = grammar_dir + grammar_name + "_aa1000M/"
        config.output_dir = path_to_aa1000M_grammar
        config.limit = 5000000
        config.attack_dict_file = "attack_dict_config"

        pcfg_mower(config)

        get_grammar_stats(grammar_name, "_aa1000M")

        ########################################################################################################
        # RUN PCFG_MOWER
        # aa500M
        path_to_aa500M_grammar = grammar_dir + grammar_name + "_aa500M/"
        config.output_dir = path_to_aa500M_grammar
        config.limit = 3000000
        config.attack_dict_file = "attack_dict_config"

        pcfg_mower(config)

        get_grammar_stats(grammar_name, "_aa500M")

        ########################################################################################################
        # RUN GO MANAGER
        output_guesses_grammar_dir = output_guesses_dir + "output_guesses/" + grammar_name + "/"
        if os.path.isdir(output_guesses_grammar_dir):
            shutil.rmtree(output_guesses_grammar_dir)
        os.mkdir(output_guesses_grammar_dir)

        for gr in res[grammar_name]:
            print("go-manager " + gr, end='\t')
            start = time.time()
            (exitcode, output) = subprocess.getstatusoutput(go_manager_dir + "pcfg-manager -r " + gr + " > " + output_guesses_grammar_dir + gr)
            elapsed = round((time.time() - start),1)
            if exitcode == 0:
                print(green("OK"))
                res[grammar_name][gr]["Time"] = elapsed
                res[grammar_name][gr]["Size"] = os.stat(output_guesses_grammar_dir + gr).st_size
                res[grammar_name][gr]["Count"] = subprocess.getoutput("wc -l " + output_guesses_grammar_dir + gr).split()[0]
            else:
                print(red("FAIL"))

        ########################################################################################################
        # RUN DICTMATCHER
        # for gr in res[grammar_name]:
        #     for ref in cracking_ref_arr:
        #         print("dictmatcher " + gr + " " + ref, end='\t')
        #         (exitcode, out) = subprocess.getstatusoutput("cd " + dictmatcher_dir + "; " + "./dictmatcher -e " + output_guesses_grammar_dir + gr + " -d " + ref + " > " +  output_guesses_grammar_dir + gr + "_dictmatcher_tmp")
        #         if exitcode == 0:
        #             print(green("OK"))
        #             (exitcode_grep, out_grep) = subprocess.getstatusoutput("grep 'Cracked' " + output_guesses_grammar_dir + gr + "_dictmatcher_tmp")
        #             if exitcode_grep == 0:
        #                 cracked = out_grep.split()[2]
        #                 res[grammar_name][gr][ref] = cracked
        #             else:
        #                 print(red("grep failed" + str(exitcode_grep)))
        #         else:
        #             print(red(exitcode))
        #             print("cd " + dictmatcher_dir + "; " + "./dictmatcher -e " + output_guesses_grammar_dir + gr + " -d " + ref)
        #             continue

        for gr in res[grammar_name]:
            for ref in cracking_ref_arr:
                res[grammar_name][gr][ref] = 42

        #print(res)

    ########################################################################################################
    # CREATE FANCY TABLE
    with open('testrun.csv', mode='w') as file:
        output_csv = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        output_csv.writerow(["Ruleset",
                             "Alpha_size",
                             "Grammar_size",
                             "Grammar_prob",
                             "Cap_size",
                             "Cap_prob",
                             "Time",
                             "Size",
                             "Count",
                             cracking_ref_arr[0],
                             cracking_ref_arr[1],
                             cracking_ref_arr[2],
                             cracking_ref_arr[3]])

        for group in res:
            for gr in res[group]:
                output_csv.writerow([gr,
                                     res[group][gr]["Alpha_size"],
                                     res[group][gr]["Grammar_size"],
                                     res[group][gr]["Grammar_prob"],
                                     res[group][gr]["Cap_size"],
                                     res[group][gr]["Cap_prob"],
                                     res[group][gr]["Time"],
                                     res[group][gr]["Size"],
                                     res[group][gr]["Count"],
                                     res[group][gr][cracking_ref_arr[0]],
                                     res[group][gr][cracking_ref_arr[1]],
                                     res[group][gr][cracking_ref_arr[2]],
                                     res[group][gr][cracking_ref_arr[3]]])

    return 0



if __name__ == "__main__":
    main()

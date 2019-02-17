#!/usr/bin/env python3

from __future__ import print_function
import sys
import argparse
from rules import Rules
from filter import Filter

if sys.version_info[0] < 3:
    print("This program requires Python 3.x", file=sys.stderr)
    sys.exit(1)



def parse_arguments(config):
    parser = argparse.ArgumentParser(description='Filters ruleset by given settings')
    parser.add_argument('--input','-i', help='Input grammar directory',required=True)
    parser.add_argument('--output','-o', help='Output grammar directory',required=True)

    try:
        args=parser.parse_args()
        config["input_dir"] = args.input
        config["output_dir"] = args.output
        config["limit"] = 6000000
        config["bs"] = float(0.02)
        config["cs"] = float(0.03)

    except Exception as msg:
        print(msg)
        return 1

    return 0

def print_ruleset_stat(rules, filter, cs):
    print("Grammar prob: " + str(filter.get_total_grammar_prob()))
    print("Grammar size: " + str(len(rules.rulesets["Grammar"])))
    print("Capitalization cs: " + str(cs))
    cap_size = 0
    for file in rules.rulesets["Capitalization"]:
        cap_size += len(rules.rulesets["Capitalization"][file])
    print("Capitalization size: " + str(cap_size))
    return 0

def main():
    config = dict()
    if parse_arguments(config):
        print("ERROR: parse_arguments", file=sys.stderr)
        return 1

    rules = Rules(config)

    if rules.load_grammar():
        print("ERROR: load_grammar", file=sys.stderr)
        return 1

    if rules.load_capitalization():
        print("ERROR: load_capitalization", file=sys.stderr)
        return 1

    if rules.load_terminals_cnt():
        print("ERROR: load_terminals_cnt", file=sys.stderr)
        return 1


    guess_cnt = rules.get_guesses_cnt()
    print(guess_cnt)
    filter = Filter(rules)

    cs = config["cs"]
    print_ruleset_stat(rules, filter, cs)

    while (guess_cnt > config["limit"]):
        filter.mow_grammar()
        filter.mow_capitalization(cs)
        guess_cnt = rules.get_guesses_cnt()
        print(guess_cnt)
        cs += config["cs"]

    print_ruleset_stat(rules, filter, cs)
    return 0



if __name__ == "__main__":
    main()

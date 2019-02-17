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
    parser.add_argument('--input','-i', help='Input grammar directory', required=True)
    parser.add_argument('--output','-o', help='Output grammar directory', required=True)
    parser.add_argument('--limit', '-l', help='Password guesses limit', required=False)

    try:
        args=parser.parse_args()
        config["input_dir"] = args.input
        config["output_dir"] = args.output
        config["bs"] = float(0.01)
        config["cs"] = float(0.01)
        if args.limit:
            config["limit"] = int(args.limit)
        else:
            config["limit"] = 500000000

    except Exception as msg:
        print(msg)
        return 1

    return 0

def print_ruleset_stat(rules, filter, cs, guess_cnt):
    print(" Guess count: " + str(guess_cnt))
    print(" Grammar prob: " + str(filter.get_total_grammar_prob()))
    print(" Grammar size: " + str(len(rules.rulesets["Grammar"])))
    print(" Capitalization cs: " + str(cs))
    cap_rules = 0
    cap_prob = 0.0
    for file in rules.rulesets["Capitalization"]:
        cap_rules += len(rules.rulesets["Capitalization"][file])
        for tuple in rules.rulesets["Capitalization"][file]:
            cap_prob += tuple[1]
    print(" Capitalization rules: " + str(cap_rules))
    print(" Capitalization files: " + str(len(rules.rulesets["Capitalization"])))
    print(" Capitalization prob: " + str(cap_prob))
    print("")
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
    if guess_cnt == -1:
        print("ERROR: get_guesses.cnt", file=sys.stderr)
        return 1

    filter = Filter(rules)
    cs = config["cs"]

    print("limit: " + str(config["limit"]))
    print("bs: " + str(config["bs"]))
    print("cs: " + str(config["cs"]))
    print("")

    print(config["input_dir"])
    print_ruleset_stat(rules, filter, cs, guess_cnt)

    while (guess_cnt > config["limit"]):
        filter.mow_grammar()
        filter.mow_capitalization(cs)
        guess_cnt = rules.get_guesses_cnt()
        #print_ruleset_stat(rules, filter, cs, guess_cnt)
        cs += config["cs"]

    print(config["output_dir"])
    print_ruleset_stat(rules, filter, cs, guess_cnt)

    if rules.save_new_grammar():
        print("ERROR: save_new_grammar", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    main()

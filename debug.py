class Debug:
    def print_ruleset(rules):
        for type in rules.rulesets.keys():
            print(" " + type)
            for file in rules.rulesets[type].keys():
                size = len(rules.rulesets[type][file])
                print("   [" + file + "]   size: " + str(size))
                print(rules.rulesets[type][file])
        return 0

    def print_ruleset_type(rules, type):
        print(" " + type)
        for file in rules.rulesets[type].keys():
            size = len(rules.rulesets[type][file])
            print("   [" + file + "]   size: " + str(size))
            print(rules.rulesets[type][file])
        return 0

    def print_ruleset_type_file(rules, type, file):
        print(" " + type)
        size = len(rules.rulesets[type][file])
        print("   [" + file + "]   size: " + str(size))
        i = 1
        for tuple in rules.rulesets[type][file]:
            print("     " + str(i) + ": " + str(tuple))
            i += 1
        return 0

    def print_dictionaries(ad):
        print(ad.priorities)
        for file in ad.dictionaries.keys():
            print(file)
            for len in ad.dictionaries[file].keys():
                print("   [" + str(len) + "] ")
                for word, prob in ad.dictionaries[file][len].items():
                    print("       " + str(word) + "  " + str(prob))

        return 0

    def print_analysed_alpha_file(self, grammar_alpha_file, top_prob, lowest_prob, lowest_prob_index, words_cnt):
        print("  [" + grammar_alpha_file + "]")
        print("      top[0]: " + str(top_prob))
        print("      low[" + str(lowest_prob_index) + "]: " + str(lowest_prob))
        print("      size: " + str(words_cnt))
        return 0

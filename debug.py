class Debug:
    def print_ruleset(rules):
        print(rules.rulesets["Alpha"]["2.txt"])
        return 0
    def print_dictionaries(ad):
        print(ad.priorities)
        for file in ad.dictionaries.keys():
            print(file)
            for len in ad.dictionaries[file].keys():
                print("   ["+str(len)+"] ")
                for word, prob in ad.dictionaries[file][len].items():
                    print("       " + str(word) +"  " + str(prob))

        return 0

    def print_analysed_alpha_file(self, grammar_alpha_file, top_prob, lowest_prob, lowest_prob_index, words_cnt):
        print("  [" + grammar_alpha_file + "]")
        print("      top[0]: " + str(top_prob))
        print("      low["+ str(lowest_prob_index) + "]: " + str(lowest_prob))
        print("      size: " + str(words_cnt))
        return 0

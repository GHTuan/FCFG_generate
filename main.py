
from nltk.grammar import FeatureGrammar

from nltk.parse.featurechart import FeatureChartParser

from nlp_generate import show_all_sentence,fcfg_generate

input_idr = "/nlp/input"
output_idr = "/nlp/output"

GRAMMAR_FILE = "/nlp/grammar.fcfg"

INPUT_SENTENCES = input_idr + "/sentences.txt"

OUTPUT_SAMPLES = output_idr + "/samples.txt"
OUTPUT_PARSE = output_idr + "/parse-results.txt"


# Step 1: Load Grammar from 'grammar.cfcg'
def load_grammar(grammar_file='grammar.cfcg'):
    with open(grammar_file, 'r', encoding='utf-8') as f:
        grammar_data = f.read()
    
    # Create CFG object
    grammar = FeatureGrammar.fromstring(grammar_data)
    # print(grammar)
    return grammar

# Generate Sentences
def generate_sentences(grammar, limit=10000, output_file=OUTPUT_SAMPLES):
    # Generate sentences using the grammar
    sentences = list(fcfg_generate(grammar, n=limit,debug=False))
    
    # Save generated sentences to a file
    with open(output_file, 'w', encoding='utf-8') as f:
        for sentence in sentences:
            f.write(' '.join(sentence) + '\n')


def parse_tree(grammar,sentences):
    parser = FeatureChartParser(grammar)
    parses_result = []
    for sentence in sentences:
        sentence = sentence.strip().split()
        parses = list(parser.parse(sentence))
        parses_result.append(parses)
    return parses_result

def read_sentences(input_file = INPUT_SENTENCES):
    with open(input_file, 'r', encoding='utf-8') as file:
        sentences = file.readlines()
    return sentences

def write_sentence(sentences, output_file=OUTPUT_PARSE):
    with open(output_file, 'w', encoding='utf-8') as file:
        for sentence in sentences:
            file.write(str(sentence) + '\n')


grammar = load_grammar(GRAMMAR_FILE)

generate_sentences(grammar,10000,OUTPUT_SAMPLES)

sentences = read_sentences(INPUT_SENTENCES)
parse_sentences = parse_tree(grammar,sentences)

write_sentence(parse_sentences,OUTPUT_PARSE)


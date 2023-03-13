import time
from textblob import TextBlob
from textblob import Word
from nltk.tokenize import word_tokenize

# TESTING THATS WHY A LOT OF PRINTS ARE PRESENT
#start time counting fot testing
start_time = time.time()

def lemmatize_tokens(tokens):
    return [Word(word).lemmatize() for word in tokens]

def keyword_check_fn(sentence, keywords):
    
    #corrected_sentence = clean_str(sentence)
    counting = 0
    tokens = word_tokenize(sentence)
    lemmatized_sentence = lemmatize_tokens(tokens)

    keyword_matches = []
    for keyword in keywords:
        keyword = keyword.lower()
        tokens = word_tokenize(keyword)
        lemmatized_keyword = lemmatize_tokens(tokens)

        if all(word in lemmatized_sentence for word in lemmatized_keyword):
            keyword_matches.append(keyword)
            counting += 1
    end_time = time.time()
    print("Time: ", end_time - start_time)
    if keyword_matches:
        print("Keyword(s) '{}' is/are present in the sentence.".format(", ".join(keyword_matches)))
        if len(keyword_matches) == len(keywords):
            print("All keywords are present in the sentence.")
    else:
        print("Keyword(s) is/are not present in the sentence.")
    return counting
# keywords = ["moan", 'Cry']
# sentence = "moans and cries while she's being touched and moved ."
# keyword_check_fn(sentence, keywords)
if __name__ == "__main__":
    pass
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
#CHANGE THIS TO ONE SENTENCE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def check_sentiment_fn(sentence):

    analyzer = SentimentIntensityAnalyzer()
    
    vs = analyzer.polarity_scores(sentence)
    

    if vs['compound'] >= 0.05:
        sentiment = "positive"
        return sentiment
    elif vs['compound'] <= -0.05:
        sentiment = "negative"
        return sentiment
    else:
        sentiment = "neutral" + str(vs['compound'])
        return sentiment
    #print("Sentiment:", sentiment)

sentences = ["AH... . IT HURTS THERE , i think i want to stop",  # positive sentence example
                "I don't want to do more. But if you want. but still, I am not ready",  # punctuation emphasis handled correctly (sentiment intensity adjusted)
                "O-okay! Just be gentle please? It hurts a bit but, if you're sure you can do this. Please go on", # booster words handled correctly (sentiment intensity adjusted)
                "no, I didn't say that! she is embarrassed . I think it's good",  # Capitalized negation
                ]
#check_sentiment_fn(sentences)
if __name__ == "__main__":
    #print each sentiment
    for sentence in sentences:
        print(check_sentiment_fn(sentence))
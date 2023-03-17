# clean response using correct_response.py
# sentimenatl analysis for animation
# keywords check for animation
import time
from keyword_checker import keyword_check_fn as keyword_check
from sentimental_testing_notoficial import check_sentiment_fn as check_sentiment

# for tests i will just use hand written text

#prompt = "she last thing he remember is going to the park with my friends. we were playing hide and seek and I hid under a bench. Then, I woke up here."
def analyzing_fn(prompt, keywords):
    print("this is your prompt: " + prompt)
    print("this is your keywords: " + str(keywords))
    sentimental = check_sentiment(prompt)

    print("to jest sentimental: " + str(sentimental))  

    counting = keyword_check(prompt, keywords)

    if sentimental == "negative" and counting > 1:
        print("negative and zaimek 'i cry' jest, running animation 'crying'")

    #main program playing animation

    # ADD ALL KEYWORDS IN IFS AND IF IT WILL PASS THEN RUN ANIMATION
    # keywords = ["i" , "cry", "she", "he", "they", "we"]
    # if analyzing_fn(prompt, keywords):
    #     print("running animation 'crying'")

while True:
    prompt = input("Enter your prompt: or 0 to end\n")
    if prompt == "0":
        break
    keywords = input("Enter your keywords: \n")
    keywords = keywords.split(",")
    analyzing_fn(prompt, keywords)


    


#keywords = ["i" , "cry", "she", "he", "they", "we"]
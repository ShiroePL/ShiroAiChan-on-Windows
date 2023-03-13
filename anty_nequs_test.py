# from profanity_check import predict, predict_prob

# print(predict(['predict() takes an array and returns a 1 for each string if it is offensive, else 0.']))
# # [0]

# print(predict(['kill']))
# # [1]

# predict_prob(['predict_prob() takes an array and returns the probability each string is offensive'])
# # [0.08686173]

# print(predict_prob(['dog']))
# [0.7618861]
from better_profanity import profanity
  
# text to be censored
text = "What the  kurwa are you doing?" # nie dziala
print(profanity.contains_profanity(text))
# do censoring
censored = profanity.censor(text)
  
# view output
print(censored)
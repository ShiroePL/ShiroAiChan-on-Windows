from shiro_agent import CustomChatAgent

def main():
    agent = CustomChatAgent()
    final_answer = agent.run("show me manga list")
    #if final_answer == "Database":
    # do something
    #print("this is fiunal answer" + final_answer)

    return final_answer

if __name__ == "__main__":
    tocos = main()
    print("to jest z returna z maina: " + tocos)



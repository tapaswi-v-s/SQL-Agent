from agent import Agent

def main():
    # Some of the examples of the queries
    # query_1 = 'I want to add a new record to the employee table.'
    # query_2 = "I want to add a new record to the employee table. The employee's first name is Tapaswi, last name is Satyapanthi and he's a Software Engineer"
    # query_3 = 'Which sales agent made the most in sales in 2009?'
    # query_4 = 'Hey! How are you doing?'
    # query_5 = "How's the weather today?"
    # query_6 = 'What this database is about?'
    # query_7 = "Update the employee Tapaswi's designation to AI Engineer"
    # query_8 = "Can you delete all the records with the name Tapaswi from the employees?"
    # query_9 = "Give me the list of all the employees."
    # query_10 = "What is the total sales?"
    # query_11 = "What is the designation of Tapaswi?"
    # query_12 = "Show me the record of the employee Tapaswi"

    # NOTE: To exit the agent, simply type exit
    agent = Agent()
    while True:
        query = input("How may I help you?: ")
        if query.strip().lower() == 'exit':
            break
        agent.execute(query)

if __name__ == "__main__":
    main()
from src.agent import Agent
from src.actions.calculate import Calculator
from src.actions.subtask_executor import SubtaskExecutor
from src.actions.execute_code import CodeExecutor
from src.actions.add_knowledge import Knowledge
from src.actions.retrieve_knowledge import Search
import re
from src.scripts.add_knowledge import *


TEST_QUERY_1 = """
We want to commision research that will provide valuable guidance to philanthropists and funders.
Consider the transcript of the episode of the 80000 hours podcast below and try to identify the one or two most pivotal questions to research as defined by the following:
1 - Which open questions most affect policy and funding recommendations? 
2 - For which questions would research yield the highest ‘value of information’?
3 - These questions should be highly specific and quantifiable such that an acacdemic study can be conducted to answer them.
4 - They should reference a topic discussed in the podcast and cite the episode and time stamp if possible.

Transcript: \n
"""

TEST_QUERY_2 = "Given the transcripts of the episode below what is the most effective intervention for helping reduce insect suffering discussed in the 80000 hours podcast? Use the search tool call to find the answer."


def test_knowledge_storage():
    calculator = Calculator()
    subtask_executor = SubtaskExecutor()
    code_executor = CodeExecutor()
    knowledge = Knowledge()
    search = Search()
    
    # Initialize agent with tools
    agent = Agent(actions=[calculator, subtask_executor, code_executor, knowledge, search])
    query_result = agent.execute_task(
        TEST_QUERY_2    
    )
    for transcript in get_files("./transcripts")[:5]:
        print(f"title: {transcript['episode_title']} length: {len(transcript['content'])}")
        query = TEST_QUERY_1 + transcript['content']
        query_result = agent.execute_task(query)
        print(f"Query Response: {query_result['response']}")


if __name__ == "__main__":
    test_knowledge_storage() 
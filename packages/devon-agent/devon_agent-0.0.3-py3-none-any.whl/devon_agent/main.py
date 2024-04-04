import openai
import os
import dotenv
from anthropic import Anthropic

from devon_agent.agent.kernel.thread import Thread
from devon_agent.sandbox.environments import LocalEnvironment

dotenv.load_dotenv()

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Process inputs for the agent.")

    parser.add_argument('--path', type=str, help='File Path', default=os.getcwd())
    parser.add_argument('--repo_url', type=str, help='GitHub Repository URL', default=None)
    parser.add_argument('--goal', type=str, help='Describe your goal')
    parser.add_argument('--question', type=str, help='Describe your question about this code base')
    args = parser.parse_args()

    repo_url = args.repo_url
    goal = args.goal
    path = args.path
    qa = False

    env = LocalEnvironment()

    if repo_url:
        env.tools.git(path=path).clone(repo_url=repo_url, path=path)
    
    if args.question:
        qa = True
        goal = args.question

    agent = Thread(task=goal, qa=qa, environment=env)

    agent.run()

if __name__ == "__main__":
    main()

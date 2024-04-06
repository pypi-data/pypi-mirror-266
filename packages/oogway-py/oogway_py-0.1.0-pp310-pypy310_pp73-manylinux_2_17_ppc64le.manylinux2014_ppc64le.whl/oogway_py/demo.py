import asyncio
import sys
import oogway_py as oogway


ai = oogway.Oogway()

# change model name from python

ai.model_name = "gpt-4-0125-preview"

async def talk_to_oogway(question: str):
    print(f"\n> You : {question}");
    while True:
        print("\n> Oogway : ", end="");
        # python async generator for chunk streaming
        async for chunk in ai.ask(question):
            sys.stdout.write(chunk)
            sys.stdout.flush()
        question = input("\n\n> You: ")

if __name__ == "__main__":
    asyncio.run(talk_to_oogway("why is life?"))

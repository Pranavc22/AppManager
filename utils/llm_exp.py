from llm import get_llm_client

def main():
    client = get_llm_client()
    response = client.chat(
        system="You are a helpful assistant.",
        user="Hello, can you give me a short greeting?"
    )
    print(response)

if __name__ == "__main__":
    main()
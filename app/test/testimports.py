try:
    from langchain_aws import BedrockEmbeddings
    print("langchain_aws imported successfully!")
except ModuleNotFoundError as e:
    print("Error:", e)

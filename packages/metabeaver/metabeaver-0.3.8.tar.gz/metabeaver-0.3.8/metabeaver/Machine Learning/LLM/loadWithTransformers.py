### Imports ###

from transformers import AutoTokenizer, AutoModelForCausalLM

### End of Imports ###


### Function Definition ###

# Given a valid path, will load a pretained model. Defaults to local search, otherwise tries HuggingFace, local, URL.
def loadPretrainedModel(configPathToModel: str, isLocalOnly=True) -> list:

    tokenizer = AutoTokenizer.from_pretrained(configPathToModel, local_files_only=isLocalOnly)
    model = AutoModelForCausalLM.from_pretrained(configPathToModel, local_files_only=isLocalOnly)

    return [tokenizer, model]

# Retrieves a tokenizer and a model, given a valid path to model directory, and responds to the LLM input string.
def runQuery(configPathToModel: str,
             inputString: str,
             isLocalOnly=True,
             max_length=512,
             repetition_penalty=1.25,
             ) -> str:

    # Try to load a valid tokenizer and model, given a location string.
    try:
        tokenizerAndModel = loadPretrainedModel(configPathToModel, isLocalOnly)
        tokenizer = tokenizerAndModel[0]
        model = tokenizerAndModel[1]

        # Take our string, turn into series of tokens, and respond to it with the Large Language Model.
        try:
            input_ids = tokenizer(inputString, return_tensors='pt')
            outputs = model.generate(**input_ids,
                                     max_length=max_length,
                                     repetition_penalty=repetition_penalty
                                     )
            print(tokenizer.decode(outputs[0]))

        # Warn that we could not load the target model with the target settings.
        except Exception as e:
            print('Could not generate a response with the loaded model!')
            print(str(e))

    # Print a warning message associated with the error that occurred.
    except Exception as e:
        print('Could not load model, an exception occurred!')
        print(str(e))
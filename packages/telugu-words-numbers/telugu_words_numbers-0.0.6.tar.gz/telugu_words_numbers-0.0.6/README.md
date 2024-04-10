## Telugu Number-Words To Numbers Conversion

### Overview
- The Telugu Number-Words to Numbers Conversion package is a Python library that enables developers to convert numerical representations written in Telugu language text (using words) into their equivalent numerical values.

### Features
- Convert Telugu number-words to numerical values.
- Supports a wide range of Telugu numerical representations.

### Create a virtual environment if require with the python version 3.8 or more
```
conda create -n telugu_num_env python=3.8

# Replace "telugu_num_env" with other name according to you
```

### Supporting packages to be installed (Additional packages can be installed if require)
```
text2digits
numpy
```

### Installation with `pip'
```
# From CMD terminal
pip install telugu-words-numbers


# From IPYNB notebook
!pip install telugu-words-numbers
```

### Inference
```
# In the CMD terminal, go to the home where inference.py is present and run it as below

$ python3 inference.py

# Note: Comment/uncomment as mentioned in the inference.py script
```


### Usage for single text conversion
```
from telugu_words_numbers import TeluguWordsToNumber

# creating and object of the class TeluguWordsToNum
converter = TeluguWordsToNumber()

text = "దీపిక కి అరవై పంపండి"
number, converted_text = converter.word_number_conversion(text)
print('Number: ', number)
print('Original Text: ', text)
print('Converted Text: ', converted_text)
```

### Out of single text conversion
```
Number:  60.0
Original Text:  దీపిక కి అరవై పంపండి
Converted Text:  దీపిక కి 60 పంపండి
```

### Usage for multiple text conversion
```
from telugu_words_numbers import TeluguWordsToNumber

# creating and object of the class TeluguWordsToNum
converter = TeluguWordsToNumber()
texts = [
            "దీపిక కి అరవై పంపండి",
            "భరత్ కి ఏడు వందలు పంపు"
    ]

for text in texts:
    number, converted_text = converter.word_number_conversion(text)
    print('Number: ', number)
    print('Original Text: ', text)
    print('Converted Text: ', converted_text)
    print('-'*20, '\n')
```

### Output of multiple text conversion
```
Number:  60.0
Original Text:  దీపిక కి అరవై పంపండి
Converted Text:  దీపిక కి 60 పంపండి
-------------------- 
Number:  700.0
Original Text:  భరత్ కి ఏడు వందలు పంపు
Converted Text:  భరత్ కి 700 పంపు
```

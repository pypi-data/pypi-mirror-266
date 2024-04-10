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
pip install telugu-words-to-number


# From IPYNB notebook
!pip install telugu-words-to-number
```

### Inference
```
# In the CMD terminal, go to the home where inference.py is present and run it as below

$ python3 inference.py

# Note: Comment/uncomment as mentioned in the inference.py script
```

### Usage

```
# For single text conversion
# Go to the path where telugu_word_to_number.py is present

from telugu_word_to_number import TeluguWordsToNumber as tel_word_num

# create an object instance
obj = tel_word_num()

text = "దీపిక కి అరవై పంపండి"
number, converted_text = obj.word_number_conversion(text)
print('Number: ', number)
print('Original Text: ', text)
print('Converted Text: ', converted_text)


# Output

Number:  60.0
Original Text:  దీపిక కి అరవై పంపండి
Converted Text:  దీపిక కి 60 పంపండి
```
```
# For multiple texts conversion loop over list of Telugu texts
# Go to the path where telugu_word_to_number.py is present

from telugu_word_to_number import TeluguWordsToNumber as tel_word_num

# create an object instance
obj = tel_word_num()

texts = [
            "దీపిక కి అరవై పంపండి",
            "భరత్ కి ఏడు వందలు పంపు"
    ]

for text in texts:
    number, converted_text = obj.word_number_conversion(text)
    print('Number: ', number)
    print('Original Text: ', text)
    print('Converted Text: ', converted_text)
    print('-'*20, '\n')

# Output

Number:  60.0
Original Text:  దీపిక కి అరవై పంపండి
Converted Text:  దీపిక కి 60 పంపండి
-------------------- 

Number:  700.0
Original Text:  భరత్ కి ఏడు వందలు పంపు
Converted Text:  భరత్ కి 700 పంపు

```

### Issues and Contributions
If you encounter any issues or would like to contribute to this project, please visit the [GitHub repository](https://github.com/Sandeep-Panchal/telugu-word-to-number-conversion/tree/main).


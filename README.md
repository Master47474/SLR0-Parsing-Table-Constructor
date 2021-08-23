# YaccOff

## A offbrand Yacc or somthn idk yet

## Running
Ensure a file named grammar.txt is inside the directory of main.py \
Then \
```
$>> python main.py
```
on the command line \
Output is of file slr0_table.json in the same directory.

## The Layout of a file
All Files will be of .txt extension \
a .txt file will consist of a "%start" on the beginning and "%end" on the last line \
**Tranches** in order of how they should be set are \
%start \
**Tokens** \
%grammar \
**Augmented Grammar** \
%end \
A program Starts with the start symbol and ends with the end symbol. a grammar symbol represents the start of the grammar declaration and the end of the tokens section. \
**Tokens** \
all tokens are of the form %token <type> identifier \
tokens : \
*production*: regex equivalent ~[a-zA-Z]*
*keyword* : regex equivalent ~[a-zA-Z]* is a string which will be treated as a reserved keyword \
*nValue* : regex equivalent [a-zA-Z_][a-zA-Z0-9_]* is a string starts with a non number and consitutes a name (for a variable or function as example) \
*iValue* : regex equivilant [0-9]* for now, we only accept integers \

**identifer** : regex equivalent [a-zA-Z_]* ; only alphabet and underscores \

**Augmented Grammar**
Where *production* is declared as a production token in the tokens section, similar to A \
So %token <production> production and %token <production> A \
The %aug indicates augmented grammar needed for creating a LR(0) Parsing table \
%aug  : production \
        ; \
production  : A '&' 'A' \
            ; \
A : '<' \
  | '>' \
  ; \

%end \

Where the | denotes are seperate body for that production and ; denotes the end of that production. \


## Output
The output will be in a JSON form, with each token as a key and their respective transitions in table. \
So Heads are "Reduce Transitions" and "Table". \
Reduce Table is of form \
```
"Reduce Transitions" : { "index" (0-n inclusive of 0 and n) : [ head, transition ] }
```
Table is of form \
```
"Table" : { "Token" : { "0": "-1 OR sx or rx or x" , "type": "typeValue", ....} }
```
Where -1 denotes no valid move from this input at this state. \
Where sx denotes to shift to state x. \
Where rx denotes to reduce using transition at position x from Reduce Transitions. \
Where x denotes what state to transition to after seeing a production head.

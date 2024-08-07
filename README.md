# ILEcst
Concrete Syntax Tree (CST) for ILE languages to train AI model and give exact conversion result

This is work in progress !!

by running the command locally on your PC ( haivng python 3.9) 

```
python extract.py --host MY_IBM_I  --pgm hello --source QGPL/QRPGLESRC  --output cst.json
```


The example of the ILE code is in "examples" folder, and you have to copy  that source to your IBM i to 
the QRPGLESRC file in QGPL

A more real life setup would be setting the library list and compile:

```
python extract.py --host MY_IBM_I  --liblist FAXUDVDB,FAXUDV,FAXUDV2924,AINCLUDE --pgm fax100 --source faxudv/qsrc  --output cst.json 
```

Note: the library list are comma seperated and no blanks are allowed.

The output - the CST and the post list are both in the repo for examination.

This is nowhere close to anything you can use, however it is a PoC and shows the idea 
of using the ILE compiler to do all the extraction needed to build the CST

This first version only produces a JSON of the global variables used in a program.

Stay tuned
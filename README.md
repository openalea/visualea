# OpenAlea.Visualea

OpenAlea.Visualea is an application that allows to use OpenAlea packages 
and to build dataflow graphically.


## License

OpenAlea.Visualea is released under a Cecill v2 license.

See LICENSE.txt
Nota : Cecill v2 license is a GPL compatible license.


## Dependence

Python >= 3.7   : http://www.python.org  
Qt >= 5.12	: http://www.trolltech.com  
PyQt >= 5.12	: https://riverbankcomputing.com/    


## Installation user mode

conda install openalea.visualea -c openalea3 -c conda-forge  


## Installation dev mode

- Create a conda environment with plantgl and pglviewer  
    
    ```
    conda create -n visualea -c openalea3 -c conda-forge openalea.plantgl pyqglviewer  
    conda activate visualea  
    conda install -c openalea3 -c conda-forge numpy scipy qtconsole pandas matplotlib openalea.sconsx networkx ipykernel ipyparallel
    ```

- clone from the openalea org

    1 core  
    2 grapheditor  
    3 openalea-components  
    4 visualea

- Checkout the visualea branch  
    `python setup.py develop`

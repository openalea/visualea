# OpenAlea.Visualea

OpenAlea.Visualea is the Visual Programming Environment of OpenAlea. It allows using OpenAlea packages 
and to build dataflow graphically.


## License

OpenAlea.Visualea is released under a Cecill v2 license.

See LICENSE.txt
Nota : Cecill v2 license is a GPL compatible license.

## Installation user mode

```bash
mamba create -n visualea -c openalea3 -c conda-forge openalea.visualea
mamba activate visualea
```

## Installation dev mode

- Clone the repository
- Use the following command
    
```bash
mamba create -f conda/environment.yml 
mamba activate visualea
```

The first command will create the *visualea* environment with the dependencies and install 
**openalea.visualea** in it with     `pip install . -e`. The second will activate the environment.


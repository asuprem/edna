# A Simple EDNA Job

Now we are ready to run a simple EDNA job. This job will connect to Twitter and stream posts to the standard output.

## Requirements

1. Twitter API account with a Bearer Token
2. Python 3.7

## Setup -- Virtual Environment

EDNA jobs use the EDNA library, located in `/python/edna`. You should use a python virtual environment while interacting with the library. If you aren't familiar with virtual environments, I recommend [this as a good first step](https://realpython.com/python-virtual-environments-a-primer/). make sure the virtual environment uses Python 3.7 or greater. [Anaconda/Miniconda is also a great option.](https://docs.conda.io/en/latest/miniconda.html). I use conda in my Windows environment and virtualenv in my bash environment

You should now create and activate a virtual environment for this project. I also recommend an IDE, since it makes working with extensions easier.

## Setup -- Library

Once you have activated a virtual environment, we'll need to install the EDNA library. However, we will do it in development mode, so any changes to the library in the repo are automatically reflected in the installed package.

First `cd` into `/python/edna`. If you do `ls`, you should see the following:

```
(edna_env) [asuprem@Suprem-Laptop: .../python/edna] $ ls
LICENSE  README.md  setup.cfg  setup.py  src  tests
```

Now install it as a development library with 

```
pip install -e .
```

Occasionally, I will push changes to the repo that will change some parts of the library. When you do git pull, the library should update itself automatically. However, new dependencies will not update automatically. So, if I add new dependencies, they will be reflected in the `setup.py` file in the `install_requires` section and require you to rerun the installation of the library.

Normally, you would do this each time you pull, but that beecomes cumbersome. So it's up to you whether you want to rerun the install with `pip install -e .` each time you pull, or run it if you get a dependency error.

# Execution

Now `cd` into `deployment-examples/TwitterSampledStreamer`. You will see a python file, 2 yaml files, and a *.dockerignore* file. Ignore (ha) the *.dockerignore* and `config.yaml`. 

Open `ednaconf.yaml` and add your Bearer Token into the Bearer Token field. You won't need the quotes. **<span style="color:maroon">Be careful in pushing any code with API keys. You don't want your API key to be on a public site.</span>**

Run the job within your virtual environment with:

```
python ./TwitterSampledStreamer.py
```

It will take a moment to set up. Then it will begin streaming to your standard output/console. Feel free to `Ctrl-C` when you are done.


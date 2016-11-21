# SXRumble

## Usage

### Requirements
Python 3.5 or later

### Installation
```
pip3 install --user -e .
```

### Cli
See `sxrumble -h`


## Development

### Setting up the environment
Using virtualenv:
```
mkvirtualenv sxrumble --python=$(which python3)
workon sxrumble
pip install -e .
pip install -r dev_requirements.txt
```

### Code check
```
./check.sh
```

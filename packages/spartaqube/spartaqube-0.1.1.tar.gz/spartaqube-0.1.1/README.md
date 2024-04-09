# <img src="https://www.spartaquant.com/assets/img/spartaquant/icon-color.png" width="60px" alt="SpartaQube icon" class="logo-default"> SpartaQube

[SpartaQube](https://www.spartaqube.com) is a plug and play solution to visualize your data and build web components

Use SpartaQube to
1. Access your data through already built-in connectors
2. Apply transformations to your data using our custom embedded Python notebook
3. Create charts and web components by dragging & dropping your transformed data

The rich user interface makes it easy to visualize and retrieve all your components

You can expose and share them with a simple html snippet code

## Installation

#### PIP INSTALL

Install the package via pip with code below:

```python
pip install spartaqube
```

To Upgrade:


```python
pip install --upgrade spartaqube
```

#### DOCKER INSTALL

Install the application via docker with the code below:

```python
docker run -p 8665:8000 spartaquant/spartaqube
```

You can change the listening port 8665 to any available port you want

Then the application runs locally and is accessible in your browser at http://localhost:8665

Get more information regarding the docker application at:
https://hub.docker.com/r/spartaqube/spartaqube


## Jupyter Notebook Integration

SpartaQube can be embedded within your usual Jupyter notebooks

Interact with your data with drag & drop and build your web components in few clicks

1. Import library
```python
from api.spartaqube import Spartaqube as Spartaqube
spartaqube_obj = Spartaqube()
```

2. List available components
```python
spartaqube_obj.get_library()
```

3. Get a specific SpartaQube widget
```python
spartaqube_obj.get_widget("<widget_id>")
```

4. Create a new component using your notebook variables
```python
spartaqube_obj.new_plot([variable1, variable2 etc...])
```

Check out the documentation of the API at https://spartaqube.com/api for more information



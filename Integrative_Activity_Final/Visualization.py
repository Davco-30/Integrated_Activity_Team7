import mesa
from mesa.visualization import SolaraViz, make_space_component
print(mesa.__version__)

# Import the local 
from Final import CityModel

def agent_portrayal(agent):
    return {
        "color": "tab:blue",
        "size": 50,
    }
model_params = {"cars":10}

propertylayer_portrayal = {
    "city_objects": {"color": "blue", "colorbar": False},
    "parking_lot": {"color": "yellow", "colorbar": False},
    "semaphores": {"color": "green", "colorbar": False},
}

# Create initial model instance
model1 = CityModel(cars=10)

SpaceGraph = make_space_component(agent_portrayal, propertylayer_portrayal=propertylayer_portrayal)
page = SolaraViz(
    model1,
    components=[SpaceGraph],
    model_params=model_params,
    name="Integrative Activity - Team7",
    
)
# This is required to render the visualization in the Jupyter notebook
page

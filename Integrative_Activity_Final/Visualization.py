import mesa
print(mesa.__version__)
from mesa.visualization import SolaraViz, make_space_component


# Importar la clase CityModel
from Final import CityModel
from Final import Car
from Final import SemaphoreAgent

def agent_portrayal(agent):
    size = 20
    color = "tab:red"
    shape = "circle"

    if isinstance(agent, Car):
        size = 50
        color = "tab:pink"
        shape = "circle"
    elif isinstance(agent, SemaphoreAgent):
        if agent.light_state == "red":
            color = "red"
            shape = "rectangular"
        if agent.light_state == "yellow":
            color = "yellow"
            shape = "rectangular"
        if agent.light_state == "green":
            color = "green"   
            shape = "rectangular" 
    return {"size": size, "color": color, "shape":shape}

# Configurar cómo se visualizan las capas de propiedades
propertylayer_portrayal = {"city_objects": {"color": "blue", "colorbar": False}}

# Crear instancia inicial del modelo
model_params = {"cars": 17}
try:
    model1 = CityModel(cars=model_params["cars"])
except TypeError as e:
    print(f"Error creating CityModel: {e}")
    print("Please check the CityModel class definition and ensure it accepts 'cars' parameter correctly.")
    exit()

# Configurar componente de visualización
SpaceGraph = make_space_component(agent_portrayal, propertylayer_portrayal=propertylayer_portrayal)
page = SolaraViz(
    model1,
    components=[SpaceGraph],
    model_params=model_params,
    name="Integrative Activity - Team7",
)
page
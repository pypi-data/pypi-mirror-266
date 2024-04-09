from pathlib import Path
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

# Tell streamlit that there is a component called presentation_card,
# and that the code to display that component is in the "frontend" folder
frontend_dir = (Path(__file__).parent / "frontend").absolute()
_component_func = components.declare_component(
	"presentation_card", path=str(frontend_dir)
)

# Create the python function that will be called
def presentation_card(
    image_path: str,
    name: str,
    post: str,
    description: str,
    key: Optional[str] = None,
):
    """
    Add a descriptive docstring
    """
    component_value = _component_func(
        image_path=image_path,
        name=name,
        post=post,
        description=description,
        key=key,
    )

    return component_value


def main():

    value = presentation_card(image_path="images/profile.png",
                              name="Abraão Andrade",
                              post="Cientista de Dados Júnior",
                              description="Atua como Pesquisador no Instituto do Cérebro UFRN e Estagiário em Análise de Dados e Automação de Processos no Supermercado Nordestão")

    st.write(value)

if __name__ == "__main__":
    main()

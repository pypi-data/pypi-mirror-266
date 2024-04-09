from pathlib import Path
from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

frontend_dir = (Path(__file__).parent / "frontend").absolute()
_component_func = components.declare_component(
	"portfolio_carousel", path=str(frontend_dir)
)

def portfolio_carousel(
    title: str,
    subtitle: str,
    cards: str,
    key: Optional[str] = None,
):
    """
    Add a descriptive docstring
    """
    component_value = _component_func(
        title=title,
        subtitle=subtitle.replace("\n", "<br>"),
        cards=cards,
        key=key,
    )

    return component_value
# print("teste")

def main():
    title = "Work"     
    subtitle =  '''Check my commercioal and non commercial projects.
               If you have any questions feel free to ask me for more information'''
    cards = [["images/zenk.jpg", "ZENK project", "Web Scraping | RPA | Data Anlysis", "https://egr1project.streamlit.app", "A formação da memória requer a expressão gênica induzida A formação da memória requer a expressão gênica induzida A formação da memória requer a expressão gênica induzida A formação da memória requer a expressão gênica induzida A formação da memória requer a expressão gênica induzida pela atividade neuronal. Esta resposta inclui uma série de genes dependentes de atividade tidos como mediadores das mudanças necessárias para a consolidação e manutenção da memória."],
             ["images/B2B.jpg", "Prospecção de Clientes B2B", "Google API | Python | Streamlit", "https://b2bprospection.streamlit.app", "Aplicação para prospectar potenciais clientes B2B no Rio Grande do Norte utilizando uma API da Google chamada Places."],
             ["images/tracking.jpg", "Bird Tracking", "Data Processing | Data Visualization", "https://birdtracking.streamlit.app", "Aplicação para processar dados de coordenadas e gerar visualizações em mapa de calor."]]
            
    value = portfolio_carousel(title=title,
                               subtitle=subtitle,
                               cards=cards)
    st.write(value)


if __name__ == "__main__":
    main()

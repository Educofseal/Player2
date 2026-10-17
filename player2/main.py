"""Ponto de entrada usado por `flet run`, `flet publish` (demo web) e `flet build` (apps nativos)."""
import flet as ft

from src.main import PASTA_ASSETS, main

if __name__ == "__main__":
    ft.run(main, assets_dir=PASTA_ASSETS)

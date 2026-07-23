#!/usr/bin/env python3
"""Punto de entrada CLI. Uso: python run.py <comando> [secuencia]"""
import sys
from carousel.pipeline import main

if __name__ == "__main__":
    main(sys.argv[1:])

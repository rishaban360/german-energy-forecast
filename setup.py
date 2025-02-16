from setuptools import setup, find_packages

setup(
    name="german-energy-forecast",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # Core Dashboard
        "dash==2.14.2",
        "Flask==2.2.5",
        "Werkzeug==2.2.3",
        "waitress==2.0.0",
        "plotly==5.18.0",
        
        # Data Processing
        "pandas==2.1.4",
        "numpy>=1.26.0",
        "python-dotenv==1.0.0",
        "entsoe-py==0.5.10",
        "holidays==0.65",
        
        # Machine Learning
        "lightgbm==4.5.0",
        "scikit-learn==1.6.1",
        
        # Jupyter Environment
        "jupyter==1.1.1",
        "jupyterlab==4.3.4",
        "notebook==7.3.2",
        "ipykernel==6.29.5",
        "ipython==8.31.0",
        
        # Visualization
        "matplotlib==3.10.0",
        "seaborn==0.13.2"
    ],
    extras_require={
        'dev': [
            "black==24.10.0",
            "flake8==7.1.1",
            "pytest==8.3.4",
            "pytest-cov==6.0.0"
        ],
        'docs': [
            "mkdocs==1.5.3",
            "mkdocs-material==9.4.6",
            "mkdocstrings==0.24.0"
        ]
    }
) 
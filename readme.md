# Alinhamento de tomografias de tórax
Repositório Minicurso XXIV SBIB 2026

### Criação do ambiente virtual e instalação de bibliotecas necessárias
    python3 -m venv pipeline-env
    source pipeline-env/bin/activate
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt

### Execução do método principal que faz o alinhamento
    python3 main.py

### Execução do algoritmo de visualização das imagens
    python3 viewMHDITK.py
  - ATENÇÂO: precisa definir manualmente o diretório raiz

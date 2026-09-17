# Alinhamento de tomografias de tórax
Repositório Minicurso XXIV SBIB 2026
- Demo de alinhamento de tomografias de tórax, não otimizado. Use apenas como guia.

### Imagens
- link para o drive: https://drive.google.com/drive/folders/10ehN_PsNWJbGPt1jJEDkTXbD5TV5oPCl?usp=sharing
- Baixe ambos os diretórios
- Coloque dentro do diretório raiz do repositório git
- Descompacte

### Criação do ambiente virtual e instalação de bibliotecas necessárias
    python3 -m venv pipeline-env
    source pipeline-env/bin/activate
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt

### Execução do método principal que faz o alinhamento
    python3 main.py

### Execução do algoritmo de visualização das imagens
    python3 viewMHDITK.py
    
### Pontos de ATENÇÂO
- Caminhos de diretórios e arquivo de parâmetros devem ser editados manualmente dentro dos códigos ou arquivo configs.json


# Large Language Models in Environmental Toxicology: Cigarette Butt Study

# Grandes Modelos de Linguagem em Toxicologia Ambiental: Estudo de Bitucas de Cigarro

Este repositório investiga a toxicidade de bitucas de cigarro (cigarette butts) usando Large Language Models (LLMs) para extração de dados.

Bitucas de cigarro são um dos resíduos mais comuns no ambiente e liberam substâncias tóxicas, incluindo metais pesados, microplásticos e compostos orgânicos. 

Modelos de linguagem (LLMs) podem ajudar a extrair dados relevantes da literatura.

# Objetivos do Projeto

Utilizar LLMs para extrair dados relevantes de artigos sobre toxicidade de bitucas de cigarro. Além disso, armazenar outros dados de nossas pesquisas.

# Pastas:
- Analisador de Pigmentação: ''analisador_pigmentacao''

# Analisador de Pigmentações

Objetivo: Esta aplicação foi feita com o intuito de analisar imagens de pigmentação de embriões de zebrafish (Danio rerio) com 96 hpf. Com base nisso, segmentar e quantificar a área pigmentada.
Requisitos: 
- Todas as imagens são permitidas, mas para melhores resultados as imagens de vista lateral dos embriões é preferível.
- As imagens devem conter uma barra de escala, para que a transformação de pixel para "mm" ou "µm" seja feita corretamente.

Funcionamento:
1. Instalar em um ambiente venv as bibliotecas do arquivo "requirements_pigmentation.txt".
2. Instalar a aplicação Tesseract-OCR, da biblioteca pytesseract [1].
3. No total temos 2 exemplos, um controle e um submetido a bituca sem tabaco remanescente (BST). Independente, o funcionamento é o mesmo.
4. Abra a imagem que você deseja, disponibilizamos as imagens na pasta "images".
5. Rode a função "recorte_manual", que abrirá uma segunda janela. Nela utilize o mouse para recortar o embrião, priorizando o máximo isolar o embrião.
6. Analise a barra de escala para obter a conversão mm/pixel, caso a barra não esteja no canto inferior direito será necessário alterar a variável "barra_escala".
7. Rode a função "ensure_head_left", que irá identificar a cabeça do embrião e irá virar para o lado esquerdo.
8. Após isso, rode a identificação da pigmentação. Caso o resultado não está satisfatório, modifique os parâmetros: "x_pig" e "y_pig"
9. Por fim, rode a conversão da área pigmentada.


# Referências:

[1] https://github.com/tesseract-ocr/tesseract

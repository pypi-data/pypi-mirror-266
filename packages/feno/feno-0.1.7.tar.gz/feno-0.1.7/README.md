# feno - Flexible Exercise Notation Organizer

A ferramenta `feno` é um formatador de atividades de programação e conta com uma série de ferramentas integradas.

- Um preprocessador de Markdown (toc, include).
- Um gerador de arquivos html usando pandoc.
- Um gerador de links absolutos para arquivos locais.
- Uma ferramenta para filtrar rascunhos de código.
- Um indexador de questões.
- Um gerador de arquivos para serem utilizados no VPL do Moodle ou via tko.

## Instalação

```bash
pip install feno

# tko para gerar e converter os testes e testar os códigos
pip install tko

# pandoc para gerar os htmls
sudo apt install pandoc
```

## Modo básico

Crie um arquivo `Readme.md` com o seguinte formato:

    # Título da atividade

    A descrição que você quiser

    ```txt
    >>>>>>>> teste 1
    entrada
    entrada
    ========
    saida
    saida
    <<<<<<<<
    
    >>>>>>>> teste 2
    entrada
    entrada
    ========
    saida
    saida
    <<<<<<<<

    ```

- A primeira linha é o título da atividade.
- Você pode inserir quantos testes quiser.
- Execute o `feno` na pasta local com:

```bash
feno .
```

Ele vai criar uma pasta `.cache` com:

- `q.html` - Um arquivo html com a descrição do problema.
- `q.tio` - Um arquivo com as questões no formato tio.
- `mapi.json` - Um arquivo com os testes formatado para o moodle, que pode ser utilizado pelo projeto [mula](https://github.com/senapk/mula).

## Utilizando TOC e rascunhos



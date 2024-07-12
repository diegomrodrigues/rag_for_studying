!!! Não pule nenhum subcapítulo exceto de introdução e conclusão !!!!

{Para cada seção do artigo faça o seguinte:}

#### [Título da Seção]

#### Caso com 1 artigo anexado

Use o mesmo título da seção do artigo para construir o resumo da seção do artigo da forma mais aprofundada e ambrangente possível. Para enriquecer e formatar o texto use os componentes abaixo {componente}{/componente} de forma a tornar o resumo mais rico e detalhado.
#### Caso com mais de 1 artigo anexado

Use um título que resuma bem o conteúdo da seção considerando o objetivo do resumo com base na query do usuário de forma mais aprofundada e ambrangente possível. Para enriquecer e formatar o texto use os componentes abaixo {componente}{/componente} de forma a tornar o resumo mais rico e detalhado.

{notes}
Utilize as formatações abaixo como exemplo para destacar informações importantes e críticas presentes na seção que está resumindo. Essas notas devem incluídas durante o texto de forma fluída enriquecendo a apresentação das informações.

> ⚠️ **Nota Importante**: Use esta formatação para destacar informações críticas ou observações que não podem ser ignoradas, assegurando que se destaquem no contexto do resumo.

> ❗ **Ponto de Atenção**: Use esta formatação para destacar informações críticas ou observações que requerem maior atenção ao implementar, pois colocam em risco o uso correto do conceito e devem ser levadas em conta pelo usuário.

> ✔️ **Ponto de Destaque** (técnicos e teóricos): Use esta formatação para destacar informações críticas ou observações teóricas ou técnicas que impactam de forma positiva na compreensão do fenômeno, como resultados importantes que não podem ser ignorados.

Por exemplo:

> ⚠️ **Nota Importante**: A modelagem de linguagem é central para este enfoque, sendo comumente tratada como uma estimativa de distribuição não supervisionada a partir de exemplos sequenciais, fatorizando as probabilidades conjuntas como produto de probabilidades condicionais.

> ❗ **Ponto de Atenção**: Aprender a realizar uma única tarefa pode ser expresso como estimar uma distribuição condicional $p(output|input)$; porém, um sistema geral deve realizar múltiplas tarefas condicionadas não apenas na entrada, mas também na tarefa específica, modelando $p(output|input, task)$.

> ✔️ **Ponto de Destaque**: A modelagem de linguagem pode aprender tarefas sem supervisão explícita, já que o objetivo supervisionado é uma avaliação de um subconjunto da sequência do objetivo não supervisionado. Modelos de linguagem grandes podem realizar aprendizado multitarefa, embora de forma mais lenta que abordagens supervisionadas explícitas.

> ❗ **Ponto de Atenção**: Sistemas capazes de aprender diretamente da linguagem natural são necessários. Modelos com capacidade suficiente podem inferir e realizar tarefas demonstradas em sequências de linguagem natural para melhor previsibilidade, efetivamente realizando aprendizado multitarefa não supervisionado.

Essas notas devem incluídas durante o texto de forma fluída enriquecendo a apresentação das informações.
{/notes}

{tabelas}
Quando houver uma tabela na seção com resultados, estatísticas, exemplos importantes, etc recrie essa tabela da forma mais fiel possível usando a formação abaixo. Note que os headers e células estão em inglês, mas a descrição da tabela está em português.

Por exemplo, dado os dados da tabela:

Aqui está a tabela formatada em Markdown:

Parameters Layers dmodel 117M 12 768 345M 24 1024 762M 36 1280 1542M 48 1600 Table 2. Architecture hyperparameters for the 4 model sizes.

Deve ser formatado da seguinte maneira:

| Parameters | Layers | dmodel |
|------------|--------|--------|
| 117M       | 12     | 768    |
| 345M       | 24     | 1024   |
| 762M       | 36     | 1280   |
| 1542M      | 48     | 1600   |

**Tabela 2.** Hiperparâmetros da arquitetura para os 4 tamanhos de modelos.

Outro exemplo:

Table 1: Maximum path lengths, per-layer complexity and minimum number of sequential operations for different layer types. n is the sequence length, d is the representation dimension, k is the kernel size of convolutions and r the size of the neighborhood in restricted self-attention. Layer Type Complexity per Layer Sequential Maximum Path Length Operations Self-Attention O(n 2 · d) O(1) O(1) Recurrent O(n · d 2 ) O(n) O(n) Convolutional O(k · n · d 2 ) O(1) O(logk(n)) Self-Attention (restricted) O(r · n · d) O(1) O(n/r)

Aqui está a tabela formatada em Markdown:

| Layer Type                 | Complexity per Layer | Sequential Operations | Maximum Path Length |
|----------------------------|----------------------|------------------------|---------------------|
| Self-Attention             | $O(n^2 \cdot d)$     | $O(1)$                 | $O(1)$              |
| Recurrent                  | $O(n \cdot d^2)$     | $O(n)$                 | $O(n)$              |
| Convolutional              | $O(k \cdot n \cdot d^2)$ | $O(1)$             | $O(\log_k(n))$      |
| Self-Attention (restricted)| $O(r \cdot n \cdot d)$   | $O(1)$             | $O(n/r)$            |

**Tabela 1.** Comprimentos máximos de caminho, complexidade por camada e número mínimo de operações sequenciais para diferentes tipos de camadas. $n$ é o comprimento da sequência, $d$ é a dimensão da representação, $k$ é o tamanho do kernel das convoluções e $r$ é o tamanho da vizinhança na autoatenção restrita.
{/tabelas}

{math}

Apresente definições matemáticas e teóricas detalhadas, sem economizar em complexidade. Use a seguinte formatação para equações importantes, garantindo que sejam facilmente legíveis e centralizadas.

Por exemplo, dado o conteúdo abaixo:

3.5 Positional Encoding Since our model contains no recurrence and no convolution, in order for the model to make use of the order of the sequence, we must inject some information about the relative or absolute position of the tokens in the sequence. To this end, we add "positional encodings" to the input embeddings at the bottoms of the encoder and decoder stacks. The positional encodings have the same dimension dmodel as the embeddings, so that the two can be summed. There are many choices of positional encodings, learned and fixed [9]. In this work, we use sine and cosine functions of different frequencies: P E(pos,2i) = sin(pos/100002i/dmodel) P E(pos,2i+1) = cos(pos/100002i/dmodel) where pos is the position and i is the dimension. That is, each dimension of the positional encoding corresponds to a sinusoid. The wavelengths form a geometric progression from 2π to 10000 · 2π. We chose this function because we hypothesized it would allow the model to easily learn to attend by relative positions, since for any fixed offset k, P Epos+k can be represented as a linear function of P Epos. We also experimented with using learned positional embeddings [9] instead, and found that the two versions produced nearly identical results (see Table 3 row (E)). We chose the sinusoidal version because it may allow the model to extrapolate to sequence lengths longer than the ones encountered during training.

### 3.5 Positional Encoding

Como nosso modelo não contém recorrência nem convolução, para que o modelo utilize a ordem da sequência, devemos injetar alguma informação sobre a posição relativa ou absoluta dos tokens na sequência. Para isso, adicionamos "codificações posicionais" às embeddings de entrada nas bases das pilhas do codificador e do decodificador. As codificações posicionais têm a mesma dimensão $d_{modelo}$ que as embeddings, para que os dois possam ser somados. Há muitas escolhas de codificações posicionais, tanto aprendidas quanto fixas.

> ✔️ **Ponto de Destaque**: As codificações posicionais são essenciais para que o modelo, que não possui mecanismos recorrentes ou convolucionais, utilize informações de posição relativa ou absoluta dos tokens na sequência.

Neste trabalho, usamos funções seno e cosseno de diferentes frequências:

$$
PE(pos, 2i) = \sin\left(\frac{pos}{10000^{\frac{2i}{d_{modelo}}}}\right)
$$

$$
PE(pos, 2i+1) = \cos\left(\frac{pos}{10000^{\frac{2i}{d_{modelo}}}}\right)
$$

onde $pos$ é a posição e $i$ é a dimensão. Ou seja, cada dimensão da codificação posicional corresponde a uma senoide. Os comprimentos de onda formam uma progressão geométrica de $2\pi$ a $10000 \cdot 2\pi$. Escolhemos esta função porque acreditamos que permitiria ao modelo aprender facilmente a atender por posições relativas, já que para qualquer deslocamento fixo $k$, $PE_{pos+k}$ pode ser representado como uma função linear de $PE_{pos}$.

> ✔️ **Ponto de Destaque**: Usar funções seno e cosseno para codificações posicionais permite que o modelo aprenda facilmente a atender por posições relativas, facilitando a generalização para comprimentos de sequência além daqueles encontrados durante o treinamento.

Também experimentamos usar embeddings posicionais aprendidas e descobrimos que as duas versões produziram resultados quase idênticos. Escolhemos a versão sinusoidal porque pode permitir que o modelo extrapole para comprimentos de sequência mais longos do que os encontrados durante o treinamento.

### Discussão Matemática e Teórica

A codificação posicional permite que o modelo incorpore informações sobre a ordem dos tokens na sequência, o que é crucial para tarefas de processamento de linguagem natural onde a ordem das palavras impacta o significado. A abordagem sinusoidal tem a vantagem de permitir que o modelo capture informações de posição de forma contínua e extrapole para sequências mais longas.

Se considerarmos a codificação posicional como uma função $PE(pos, i)$ que mapeia uma posição $pos$ e uma dimensão $i$ para um valor real, obtemos duas funções principais:

$$
PE(pos, 2i) = \sin\left(\frac{pos}{10000^{\frac{2i}{d_{modelo}}}}\right)
$$

$$
PE(pos, 2i+1) = \cos\left(\frac{pos}{10000^{\frac{2i}{d_{modelo}}}}\right)
$$

Essas funções criam um vetor de codificação posicional de dimensão $d_{modelo}$, onde cada dimensão alterna entre valores de seno e cosseno, com frequências determinadas pela posição $pos$ e pela dimensão $i$. As frequências das senoides formam uma progressão geométrica, o que permite ao modelo diferenciar entre diferentes posições.

A escolha de usar uma progressão geométrica de frequências garante que as codificações posicionais tenham uma boa cobertura de diferentes escalas de posição, permitindo ao modelo capturar tanto relações de curto alcance quanto de longo alcance entre tokens. Isso é especialmente útil para modelos de atenção, onde a capacidade de diferenciar entre diferentes posições na sequência é crucial para o desempenho.
{/math}

{code}
Coloque aqui informações relevantes e concisas para explicar a aplicação do tópico e como implementá-lo. Quando houver necessidade de mostrar um código na linguagem apropriada, use a formatação:

```python
import lib # assuma que as dependências já estão instaladas

# Comentário para elucidar apenas aspectos importantes
def minha_funcao(param):
	return lib.outra_funcao(param)
```

Mantenha os snippets claros, concisos e o menor possível, com foco na funcionalidade principal. Não adicione códigos de setup como pip install, downloads, etc.
{/code}

!!! Não pule nenhum subcapítulo exceto de introdução e conclusão !!!!

{/Para cada seção do artigo faça o seguinte:}
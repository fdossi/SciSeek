# Search Syntax

## Simple
Lista de termos literais independentes.

Exemplo:
`alpha,beta,gamma`

## Regex
Cada termo e compilado como regex.
Regex invalida gera erro de validacao.

Exemplo:
`micro(plastic|plastico)`

## Proximity
Verifica pares consecutivos de termos e conta ocorrencias quando a distancia maxima em palavras e respeitada.

Exemplo:
termos: `microplastic,tendon`
distancia: `10`

## Boolean
Parser com precedencia:
1. NOT
2. AND
3. OR

Suporta parenteses.

Exemplos validos:
- `(alpha OR beta) AND NOT gamma`
- `microplastic AND tendon`

Exemplos invalidos:
- `AND alpha`
- `(alpha OR beta`

# IJVM Instruction Set

<br>

| KEYWORDS      | OPERANDI               | DESCRIZIONE                                                                                           |
|---------------|------------------------|-------------------------------------------------------------------------------------------------------|
| BIPUSH        | **byte** (dec/oct/hex) | Mette un byte in cima nello stack.                                                                    |
| DUP           | 🞬                     | Duplica il byte in cima allo stack, **BIPUSH** della copia.                                           |
| ERR           | 🞬                     | Stampa un messaggio di errore e **HALT**.                                                             |
| GOTO          | **label**              | Salta incondizionalmente.                                                                             |
| HALT          | 🞬                     | Blocca l'esecuzione del programma.                                                                    |
| IADD          | 🞬                     | **POP** di due parole e **PUSH** della somma.                                                         |
| IAND          | 🞬                     | **POP** di due parole e **PUSH** "boolean AND".                                                       |
| IFEQ          | **label**              | **POP** di una parola e **GOTO** alla **label** se il valore della parola e' zero.                    |
| IFLT          | **label**              | **POP** di una parola e **GOTO** alla **label** se il valore della parola e' minore di zero.          |
| IF_ICMPEQ     | **label**              | **POP** di due parole e **GOTO** alla **label** se sono equivalenti.                                  |
| IINC          | **var name, byte**     | Somma un byte ad una variabile locale.                                                                |
| ILOAD         | **var name**           | **BIPUSH** di una variabile.                                                                          |
| IN            | 🞬                     | Legge e **BIPUSH** di un carattere dall'input. Se non e' disponibile alcun carattere, **BIPUSH 0x0**. |
| INVOKEVIRTUAL | **method**             | Invoca un metodo, **POP** dell'oggetto e degli eventuali argomenti del metodo.                        |
| IOR           | 🞬                     | **POP** di due parole e **PUSH** "boolean OR".                                                        |
| IRETURN       | 🞬                     | Ritorna dal metodo con un valore intero.                                                              |
| ISTORE        | **variable**           | **POP** di una parola e memorizzazione in una variabile.                                              |
| ISUB          | 🞬                     | **POP** di due parole sottrae la seconda parola con la prima, **BIPUSH** della differenza.            |
| LDC_W         | **constant**           | **BIPUSH** di una costante.                                                                           |
| NOP           | 🞬                     | Non fa nulla.                                                                                         |
| OUT           | 🞬                     | **POP** di una parola e stampa il carattere corrispondente.                                           |
| POP           | 🞬                     | Rimozione di una parola dalla cima dello stack.                                                       |
| SWAP          | 🞬                     | Scambia le prime due parole nello stack.                                                              |
| WIDE          | 🞬                     | Estende il formato di un'istruzione. (!!)                                                             |

(!!) L'istruzione **WIDE** non e' stata implementata nell'interprete IJVM, dato che nell'anno accademico 2021/2022 non e' stata utilizzata.
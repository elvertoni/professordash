# Aula 01 — Internet e o funcionamento da Web

Você usa a internet todos os dias para estudar, se comunicar, assistir vídeos
e jogar. Mas você sabe o que acontece entre o momento em que digita um
endereço no navegador e a página aparecer na tela? Nesta aula, vamos
desvendar os conceitos fundamentais que fazem a web funcionar: a arquitetura
cliente-servidor, os protocolos HTTP e HTTPS, o sistema de nomes DNS e o
papel de cada componente nessa engrenagem. Entender esses fundamentos é
o primeiro passo para se tornar um desenvolvedor web consciente.

## Como a internet funciona

A internet é uma rede global de computadores interconectados que se comunicam por meio de protocolos padronizados. Imagine um sistema de correios digital: cada computador tem um endereço único (o endereço IP), e os dados são divididos em pacotes que viajam por caminhos diferentes até chegar ao destino.

:::conceito Internet
Rede mundial de redes de computadores que utilizam o conjunto de
protocolos TCP/IP para se comunicar. Não é a mesma coisa que a World
Wide Web — a web é um dos serviços que rodam sobre a internet, assim
como email e streaming.
:::

Cada dispositivo conectado à internet recebe um endereço IP (Internet Protocol), que funciona como um número de telefone. No protocolo IPv4, esse número tem o formato `192.168.1.1`. Como decorar números é difícil, criamos um sistema de nomes amigáveis: os domínios.

## Modelo cliente-servidor

A web funciona no modelo cliente-servidor. O cliente (seu navegador) faz requisições, e o servidor (um computador remoto) processa e devolve respostas.

:::importante Cliente vs Servidor
O cliente é quem inicia a comunicação — geralmente o navegador
(Chrome, Firefox, Edge). O servidor é um computador que fica ligado
24/7 esperando requisições e respondendo com os recursos solicitados
(HTML, CSS, imagens, dados).
:::

O fluxo básico é:
1. Você digita `https://aulas.tonicoimbra.com` no navegador.
2. O navegador consulta o DNS para descobrir o IP do servidor.
3. O navegador envia uma requisição HTTP para esse IP.
4. O servidor processa e envia de volta uma resposta (a página HTML).
5. O navegador renderiza o HTML na tela.

## HTTP e HTTPS — a linguagem da web

HTTP (Hypertext Transfer Protocol) é o protocolo que define como cliente e servidor se comunicam. Toda requisição tem um método (GET, POST, PUT, DELETE), um caminho (URL) e cabeçalhos. Toda resposta tem um código de status (200, 404, 500) e o conteúdo.

:::conceito HTTPS
HTTPS é a versão segura do HTTP. Os dados são criptografados usando
SSL/TLS antes de viajar pela rede. É por isso que você vê o cadeado
verde ao lado do endereço — ele indica que ninguém no meio do caminho
pode ler os dados transmitidos.
:::

:::curiosidade Os códigos de status mais famosos
O erro 404 (Not Found) é o mais conhecido, mas não é o único. 200
significa sucesso, 301 é redirecionamento permanente, 403 é acesso
proibido e 500 é erro interno do servidor. Cada faixa tem um significado:
1xx = informação, 2xx = sucesso, 3xx = redirecionamento, 4xx = erro do
cliente, 5xx = erro do servidor.
:::

## Questões de fixação

:::questao Qual é a função do protocolo HTTPS em relação ao HTTP comum?
a) HTTPS é mais rápido que HTTP porque usa menos cabeçalhos
b) HTTPS criptografa os dados transmitidos entre cliente e servidor *
c) HTTPS substitui o DNS, eliminando a necessidade de consulta de IP
d) HTTPS funciona apenas em conexões de fibra óptica
> O HTTPS (Hypertext Transfer Protocol Secure) adiciona uma camada de
> criptografia SSL/TLS sobre o HTTP. Isso garante que os dados trafegados
> não possam ser lidos por intermediários, protegendo informações como
> senhas e dados de cartão de crédito. A velocidade é similar ao HTTP,
> e o DNS continua sendo necessário independentemente do protocolo.
:::

:::questao Qual das alternativas NÃO corresponde a uma etapa do fluxo de carregamento de uma página web?
a) O navegador consulta o DNS para obter o endereço IP do servidor
b) O navegador envia uma requisição HTTP GET para o servidor
c) O servidor compila o código-fonte diretamente no disco rígido do cliente *
d) O servidor responde com o conteúdo HTML e o navegador renderiza a tela
> A compilação de código-fonte no disco rígido do cliente não faz parte do
> fluxo de carregamento de páginas web. O navegador apenas interpreta e
> renderiza o HTML, CSS e JavaScript recebidos do servidor. Todas as outras
> etapas (consulta DNS, requisição HTTP, resposta do servidor, renderização)
> são partes reais e essenciais do processo.
:::

## DNS — a agenda telefônica da internet

O DNS (Domain Name System) traduz nomes de domínio legíveis por humanos (`google.com`) em endereços IP (`142.250.218.78`) que os computadores entendem.

:::exemplo Como o DNS resolve um domínio
Quando você digita "google.com", seu computador pergunta ao DNS
"qual o IP de google.com?" e recebe de volta "142.250.218.78".
Sem o DNS, você teria que memorizar dezenas de números para acessar
qualquer site.
:::

O sistema é hierárquico: existem servidores DNS raiz, servidores de domínio de topo (.com, .org, .br) e servidores autoritativos para cada domínio específico. Quando um DNS não sabe a resposta, ele pergunta ao próximo nível acima.

## Atividade prática

Vamos usar as ferramentas do próprio navegador para ver o modelo cliente-servidor funcionando ao vivo.

:::objetivo Entrega
Abra o DevTools do navegador (F12), vá até a aba "Rede" (Network),
recarregue esta página e identifique: (1) o código de status da resposta,
(2) o método HTTP usado, (3) o tempo total de carregamento. Print da
tela. Salve como `aula01-investigacao-rede.png`.
:::

:::roteiro
Pessoal, essa atividade é tipo abrir o capô de um carro pela primeira
vez. Vocês vão ver todas as requisições que o navegador faz — HTML,
CSS, JS, imagens — cada uma com seu status. Não precisa entender tudo
agora, só observar que o navegador não faz mágica: são dezenas de
requisições cliente-servidor em milissegundos.
:::

## Fechamento

:::resumo
- A internet é uma rede global de computadores; a web é um serviço que
  roda sobre ela
- No modelo cliente-servidor, o navegador requisita e o servidor responde
- HTTP é o protocolo de comunicação; HTTPS adiciona criptografia
- Próxima aula: criando sua primeira página com HTML
:::

# TODO: Lidar com casos de o git não estar instalado e do diretório de destino do clone não estar vazio.

# Criando diretórios DEV, TEST, UAT, PRODUCTION
mkdir -v DEV TEST UAT PRODUCTION

# Perguntando URL do projeto (digitar https://github.com/jfsc/spring-petclinic.git)
echo "Digite a URL do projeto: "
read url
cd DEV
git clone $url
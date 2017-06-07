# TODO: 1) Lidar com casos de o git não estar instalado, 2) do diretório de destino do clone (DEV/<PASTA_DO_PROJETO>) não estar vazio,
# 3) de não ter o java instalado, 4) de não ter a variavel de ambiente JAVA_HOME setada, 5) de não ter o maven ou o junit instalado.

# Criando diretórios DEV, TEST, UAT, PRODUCTION
mkdir -v DEV TEST UAT PRODUCTION

# Perguntando URL do projeto (digitar https://github.com/jfsc/spring-petclinic.git) e clonando no diretório DEV
echo "Digite a URL do projeto: "
read url
cd DEV
git clone $url && cd $(basename $_ .git)

# Compilando e testando o junit
mvn clean install
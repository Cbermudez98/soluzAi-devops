// Pipeline de Entrega Continua (CD) de SoporteIA API.
//
// Se ejecuta cuando un cambio llega a main (después de que el CI de GitHub
// Actions lo validó). Construye una imagen inmutable etiquetada con el commit,
// la escanea, la publica en un registro y la despliega en Kubernetes.
//
// Es agnóstico al entorno: el registro (Docker Hub, Artifact Registry, ECR,
// ACR...) y el clúster (GKE, EKS, AKS, minikube...) se eligen con parámetros
// y credenciales de Jenkins, sin cambiar el código.
//
// Requisitos del agente: git, docker, python3, trivy y kubectl.
// Credenciales en Jenkins:
//   - registry-credentials (usuario/contraseña o token del registro)
//   - kubeconfig           (archivo secreto con acceso al clúster)

pipeline {
    agent any

    parameters {
        string(name: 'REGISTRY', defaultValue: 'docker.io',
               description: 'Registro de imágenes (docker.io, us-central1-docker.pkg.dev, ...)')
        string(name: 'IMAGE_REPO', defaultValue: 'cbermudez98/soporteia-api',
               description: 'Repositorio de la imagen dentro del registro')
        choice(name: 'DEPLOY_ENV', choices: ['staging', 'production'],
               description: 'Namespace de Kubernetes destino')
        booleanParam(name: 'SKIP_DEPLOY', defaultValue: false,
                     description: 'Solo construir y publicar la imagen, sin desplegar')
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = "${params.REGISTRY}/${params.IMAGE_REPO}"
        APP_NAME   = 'soporteia-api'
    }

    stages {
        // 1. Obtiene exactamente el commit que disparó el pipeline.
        stage('Clonar repositorio') {
            steps {
                checkout scm
                script {
                    env.GIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    env.IMAGE_TAG = "${env.IMAGE_NAME}:${env.GIT_SHORT}"
                }
                echo "Commit ${env.GIT_SHORT} -> imagen ${env.IMAGE_TAG}"
            }
        }

        // 2. Red de seguridad: no se publica nada que no pase las pruebas,
        //    aunque alguien dispare el pipeline a mano sin pasar por el CI.
        stage('Pruebas') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/pip install -q -r requirements-dev.txt
                    .venv/bin/ruff check .
                    .venv/bin/pytest -q --junitxml=reports/junit.xml
                '''
            }
            post {
                always { junit allowEmptyResults: true, testResults: 'reports/junit.xml' }
            }
        }

        // 3. Imagen inmutable: la etiqueta es el commit, así lo que se prueba
        //    en staging es exactamente lo que llega a producción.
        stage('Construir imagen Docker') {
            steps {
                sh '''
                    docker build \
                      --label org.opencontainers.image.revision=${GIT_SHORT} \
                      -t ${IMAGE_TAG} -t ${IMAGE_NAME}:latest .
                '''
            }
        }

        // 4. Bloquea la publicación si la imagen tiene CVE críticas.
        stage('Escanear imagen (Trivy)') {
            steps {
                sh 'trivy image --severity CRITICAL --ignore-unfixed --exit-code 1 --no-progress ${IMAGE_TAG}'
            }
        }

        // 5. Publica la imagen en el registro configurado.
        stage('Publicar imagen') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'registry-credentials',
                                                  usernameVariable: 'REG_USER',
                                                  passwordVariable: 'REG_PASS')]) {
                    sh '''
                        echo "$REG_PASS" | docker login ${REGISTRY} -u "$REG_USER" --password-stdin
                        docker push ${IMAGE_TAG}
                        docker push ${IMAGE_NAME}:latest
                    '''
                }
            }
        }

        // 6. Despliega en el namespace elegido y espera a que el rollout
        //    termine sano (readiness probe en /health).
        stage('Desplegar en Kubernetes') {
            when {
                allOf {
                    branch 'main'
                    expression { !params.SKIP_DEPLOY }
                }
            }
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    sh '''
                        kubectl create namespace ${DEPLOY_ENV} --dry-run=client -o yaml | kubectl apply -f -
                        kubectl apply -n ${DEPLOY_ENV} -f k8s/
                        kubectl set image -n ${DEPLOY_ENV} deployment/${APP_NAME} api=${IMAGE_TAG}
                        kubectl rollout status -n ${DEPLOY_ENV} deployment/${APP_NAME} --timeout=180s
                    '''
                }
            }
        }

        // 7. Verifica el servicio desde dentro del clúster.
        stage('Smoke test') {
            when {
                allOf {
                    branch 'main'
                    expression { !params.SKIP_DEPLOY }
                }
            }
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    sh '''
                        kubectl run smoke-${GIT_SHORT} -n ${DEPLOY_ENV} --rm -i --restart=Never \
                          --image=curlimages/curl:8.11.1 -- \
                          curl -fsS http://${APP_NAME}/health
                    '''
                }
            }
        }
    }

    post {
        failure {
            // Si el despliegue falló, vuelve a la versión anterior.
            script {
                if (env.BRANCH_NAME == 'main' && !params.SKIP_DEPLOY) {
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                        sh 'kubectl rollout undo -n ${DEPLOY_ENV} deployment/${APP_NAME} || true'
                    }
                }
            }
        }
        always {
            sh 'docker logout ${REGISTRY} || true'
            sh 'docker rmi ${IMAGE_TAG} ${IMAGE_NAME}:latest || true'
            cleanWs()
        }
    }
}

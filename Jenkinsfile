// Continuous Delivery (CD) pipeline for SoporteIA API.
//
// Runs when a change reaches main (after GitHub Actions CI has validated it).
// Builds an immutable image tagged with the commit, scans it, publishes it to
// a registry and deploys it to Kubernetes.
//
// Environment-agnostic: the registry (Docker Hub, Artifact Registry, ECR,
// ACR...) and the cluster (GKE, EKS, AKS, minikube...) are selected through
// Jenkins parameters and credentials, without changing the code.
//
// Agent requirements: git, docker, python3, trivy and kubectl.
// Jenkins credentials:
//   - registry-credentials (registry username/password or token)
//   - kubeconfig           (secret file with cluster access)

pipeline {
    agent any

    parameters {
        string(name: 'REGISTRY', defaultValue: 'docker.io',
               description: 'Image registry (docker.io, us-central1-docker.pkg.dev, ...)')
        string(name: 'IMAGE_REPO', defaultValue: 'cbermudez98/soporteia-api',
               description: 'Image repository inside the registry')
        choice(name: 'DEPLOY_ENV', choices: ['staging', 'production'],
               description: 'Target Kubernetes namespace')
        booleanParam(name: 'SKIP_DEPLOY', defaultValue: false,
                     description: 'Only build and publish the image, do not deploy')
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
        // 1. Fetch exactly the commit that triggered the pipeline.
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_SHORT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    env.IMAGE_TAG = "${env.IMAGE_NAME}:${env.GIT_SHORT}"
                }
                echo "Commit ${env.GIT_SHORT} -> image ${env.IMAGE_TAG}"
            }
        }

        // 2. Safety net: nothing is published unless tests pass, even if
        //    someone triggers the pipeline manually without going through CI.
        stage('Test') {
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

        // 3. Immutable image: the tag is the commit, so what is tested in
        //    staging is exactly what reaches production.
        stage('Build Docker image') {
            steps {
                sh '''
                    docker build \
                      --label org.opencontainers.image.revision=${GIT_SHORT} \
                      -t ${IMAGE_TAG} -t ${IMAGE_NAME}:latest .
                '''
            }
        }

        // 4. Block publishing if the image has critical CVEs.
        stage('Scan image (Trivy)') {
            steps {
                sh 'trivy image --severity CRITICAL --ignore-unfixed --exit-code 1 --no-progress ${IMAGE_TAG}'
            }
        }

        // 5. Publish the image to the configured registry.
        stage('Push image') {
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

        // 6. Deploy to the selected namespace and wait for a healthy rollout
        //    (readiness probe on /health).
        stage('Deploy to Kubernetes') {
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

        // 7. Verify the service from inside the cluster.
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
            // If the deployment failed, roll back to the previous version.
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

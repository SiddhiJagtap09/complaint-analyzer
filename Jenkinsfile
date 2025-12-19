pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: dind
    image: docker:dind
    securityContext:
      privileged: true
    env:
    - name: DOCKER_TLS_CERTDIR
      value: ""

  - name: kubectl
    image: bitnami/kubectl:latest
    command: ["sh", "-c", "sleep 3600"]
    tty: true
    env:
    - name: KUBECONFIG
      value: /kube/config
    volumeMounts:
    - name: kubeconfig-secret
      mountPath: /kube/config
      subPath: kubeconfig

  volumes:
  - name: kubeconfig-secret
    secret:
      secretName: kubeconfig-secret
'''
        }
    }

    environment {
        APP_NAME      = "complaint-analyzer"
        IMAGE_TAG     = "latest"
        REGISTRY_URL  = "nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
        REGISTRY_REPO = "2401070"
        K8S_NAMESPACE = "241010710"
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                container('dind') {
                    sh '''
                        sleep 10
                        docker build -t $APP_NAME:$IMAGE_TAG .
                        docker images
                    '''
                }
            }
        }

        stage('Run Tests') {
            steps {
                echo "Skipping tests (database not available in CI environment)"
            }
        }

        stage('Docker Login') {
            steps {
                container('dind') {
                    sh '''
                        docker login http://nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085 \
                        -u admin -p Changeme@2025 || true
                    '''
                }
            }
        }

        stage('Build - Tag - Push Image') {
            steps {
                container('dind') {
                    sh '''
                        docker tag $APP_NAME:$IMAGE_TAG \
                        $REGISTRY_URL/$REGISTRY_REPO/$APP_NAME:$IMAGE_TAG

                        docker push $REGISTRY_URL/$REGISTRY_REPO/$APP_NAME:$IMAGE_TAG || true
                    '''
                }
            }
        }

        stage('Deploy Application') {
            steps {
                container('kubectl') {
                    sh 'kubectl apply -f k8s/deployment.yaml -n 241010710'
                    sh 'kubectl rollout status deployment/complaint-analyzer -n 241010710'
                }
            }
        }
    }
}

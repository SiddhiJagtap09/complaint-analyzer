pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: kubectl
    image: bitnami/kubectl:latest
    command:
      - cat
    tty: true
    securityContext:
      runAsUser: 0
      readOnlyRootFilesystem: false
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
        K8S_NAMESPACE = "2410710"
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                container('kubectl') {
                    sh '''
                        kubectl version --client

                        # Create namespace if it does not exist
                        kubectl create namespace $K8S_NAMESPACE || true

                        kubectl apply -f k8s/deployment.yaml -n $K8S_NAMESPACE
                        kubectl rollout status deployment/complaint-analyzer -n $K8S_NAMESPACE
                    '''
                }
            }
        }
    }
}

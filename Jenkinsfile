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
        K8S_NAMESPACE = "2401070"
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

                        kubectl create namespace $K8S_NAMESPACE || true

                        # APPLY ALL FILES (deployment + service + ingress)
                        kubectl apply -f k8s/ -n $K8S_NAMESPACE

                        kubectl rollout status deployment/complaint-analyzer -n $K8S_NAMESPACE
                    '''
                }
            }
        }
    }
}

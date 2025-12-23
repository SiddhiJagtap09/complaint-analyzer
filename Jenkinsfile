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

                # Create namespace if not exists
                kubectl create namespace 2410710 || true

                kubectl apply -f k8s/deployment.yaml -n 2410710
                kubectl rollout status deployment/complaint-analyzer -n 2410710
            '''
        }
    }
}

    }
}

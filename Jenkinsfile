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
    - sh
    - -c
    - cat
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
        K8S_NAMESPACE = "2410710"
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Build Stage') {
            steps {
                echo "Build skipped: Docker not allowed on this cluster"
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                container('kubectl') {
                    sh '''
                        echo "Checking kubectl..."
                        kubectl version --client

                        echo "Checking namespaces..."
                        kubectl get ns

                        echo "Deploying application..."
                        kubectl apply -f k8s/deployment.yaml -n 2410710

                        echo "Waiting for rollout..."
                        kubectl rollout status deployment/complaint-analyzer -n 2410710
                    '''
                }
            }
        }
    }
}

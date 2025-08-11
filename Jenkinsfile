pipeline {
  agent any

  environment {
    ENV = "unit-test"
    IMAGE_NAME = "assignments-ci"
  }

  stages {
    stage('Build CI Image') {
      steps {
        echo "Contruzione immagine da Dockerfile.ci..."
        sh '''
          docker build -t ${IMAGE_NAME} -f Dockerfile.ci .
        '''
      }
    }

    stage('Run Python Unit Tests') {
      steps {
        echo "Avvio container CI per i unit-test..."
        sh '''
          docker run --rm  -e ENV="unit-test" -v "${PWD}:/work"  -w /work assignments-ci pytest -v test/pytest
        '''
      }
    }
  }

  post {
    success { echo "Tutti i test passati!" }
    failure { echo "I test sono falliti." }
  }
}

pipeline {
  agent any

  environment {
    ENV = "test"
    COMPOSE_FILE = "docker-compose.test.yml"
    TEST_SECRETS_PATH = "/home/jenkins-user/secrets/assignment-test"
  }

  stages {

    stage('Setup environment') {
      steps {
        echo "🔧 Copio i secrets nella workspace..."
        sh '''
          cp $TEST_SECRETS_PATH/.env.test .env.test
          mkdir -p secrets
          cp $TEST_SECRETS_PATH/public.pem secrets/public.pem
          cp $TEST_SECRETS_PATH/private.pem secrets/private.pem
        '''
      }
    }

    stage('Build & start test environment') {
      steps {
        sh 'docker-compose -f $COMPOSE_FILE up -d --build'
      }
    }

    stage('Run API Tests with Newman') {
      steps {
        sh '''
          newman run ./test/postman/Assignments.postman_collection.json \
            -e ./test/postman/Assignments.postman_environment.json \
            --reporters cli,json
        '''
      }
    }

    stage('Tear down environment') {
      steps {
        sh 'docker-compose -f $COMPOSE_FILE down'
      }
    }
  }

  post {
    always {
      echo "🧼 Pulizia finale..."
      //deleteDir() // Pulisce la workspace
    }
    success {
      echo "✅ Build e test completati con successo!"
    }
    failure {
      echo "❌ Qualcosa è andato storto."
    }
  }
}

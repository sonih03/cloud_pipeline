pipeline {
    agent any

    environment {
        // Jenkins Credentials에 등록할 ID 이름들
        DOTENV_CREDENTIAL_ID = 'project-dotenv-file'      // Secret file 형식 (.env)
        AWS_SSH_CREDENTIAL_ID = 'aws-ec2-ssh-key'        // SSH Username with private key 형식

        // AWS 배포 타겟 서버 정보
        AWS_EC2_USER = 'ubuntu'
        AWS_EC2_HOST = '3.38.41.74'
        REMOTE_DIR   = '/home/ubuntu/project'
    }

    stages {
        stage('1. Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('2. Inject .env Secrets') {
            steps {
                // Jenkins Secret File에서 .env 주입
                withCredentials([file(credentialsId: env.DOTENV_CREDENTIAL_ID, variable: 'SECRET_ENV')]) {
                    sh 'cp $SECRET_ENV .env'
                }
            }
        }

        stage('3. Deploy to AWS EC2') {
            steps {
                sshagent([env.AWS_SSH_CREDENTIAL_ID]) {
                    sh """
                        # 1. EC2 원격 디렉토리 생성
                        ssh -o StrictHostKeyChecking=no ${AWS_EC2_USER}@${AWS_EC2_HOST} "mkdir -p ${REMOTE_DIR}"

                        # 2. 소스코드 및 .env 동기화 (rsync 사용)
                        rsync -avz --exclude '.git' --exclude 'backend/.venv' --exclude 'frontend/node_modules' ./ ${AWS_EC2_USER}@${AWS_EC2_HOST}:${REMOTE_DIR}/

                        # 3. Docker Compose 빌드 및 무중단 재배포
                        ssh -o StrictHostKeyChecking=no ${AWS_EC2_USER}@${AWS_EC2_HOST} "
                            cd ${REMOTE_DIR} &&
                            docker compose down &&
                            docker compose up --build -d &&
                            docker image prune -f
                        "
                    """
                }
            }
        }
    }

    post {
        success {
            echo '배포가 성공적으로 완료되었습니다!'
        }
        failure {
            echo '배포 파이프라인 실행 중 에러가 발생했습니다.'
        }
    }
}
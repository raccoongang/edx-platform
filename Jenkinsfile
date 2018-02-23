#!groovy

timeout_ci = env.CI_TIMEOUT.toInteger() ?: 35
assert timeout_ci instanceof Integer
channel_name = env.CHANNEL_NAME ?: "ci-open-edx"


def startTests(suite, shard) {
        return {
                timeout(timeout_ci.toInteger()) {
                        node("${suite}-${shard}-worker") {
                                wrap([$class: 'AnsiColorBuildWrapper', 'colorMapName': 'XTerm', 'defaultFg': 1, 'defaultBg': 2]) {
                                        cleanWs()
                                        checkout scm
                                        try {
                                                withEnv(["TEST_SUITE=${suite}", "SHARD=${shard}"]) {
                                                        sh './scripts/all-tests.sh'
                                                }
                                        } catch (err) {
                                                slackSend channel: channel_name, color: 'danger', message: "Test ${suite}-${shard} failed in ${env.JOB_NAME}. Please check build info. (<${env.BUILD_URL}|Open>)", teamDomain: 'raccoongang', tokenCredentialId: 'slack-secret-token'
                                        } finally {
                                                archiveArtifacts 'reports/**, test_root/log/**'
                                                stash includes: 'reports/**, test_root/log/**', name: "artifacts-${suite}-${shard}"
                                                junit 'reports/**/*.xml'
                                                deleteDir()
                                        }
                                }
                        }
                }
        }
}

def coverageTest() {
        node('coverage-report-worker') {
                wrap([$class: 'AnsiColorBuildWrapper', 'colorMapName': 'XTerm', 'defaultFg': 1, 'defaultBg': 2]) {
                        cleanWs()
                        checkout scm
                        try {
                                unstash 'artifacts-lms-unit-1'
                                unstash 'artifacts-lms-unit-2'
                                unstash 'artifacts-lms-unit-3'
                                unstash 'artifacts-lms-unit-4'
                                unstash 'artifacts-cms-unit-all'
                                withCredentials([string(credentialsId: 'rg-codecov-edx-platform-token', variable: 'CODE_COV_TOKEN')]) {
                                        sh "git rev-parse --short HEAD^1 > .git/ci-branch-id"
                                        sh "git rev-parse --short HEAD^2 > .git/target-branch-id"
                                        def CI_BRANCH = readFile('.git/ci-branch-id')
                                        def TARGET_BRANCH = readFile('.git/target-branch-id')
                                        sh './scripts/jenkins-report.sh'
                                }
                        } finally {
                                archiveArtifacts 'reports/**, test_root/log/**'
                                cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'reports/coverage.xml', conditionalCoverageTargets: '70, 0, 0', failUnhealthy: false, failUnstable: false, lineCoverageTargets: '80, 0, 0', maxNumberOfBuilds: 0, methodCoverageTargets: '80, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
                                deleteDir()
                        }
                }
        }
}

def getSuites() {
        return [
                [name: 'lms-unit', 'shards': [
                1,
                2,
                3,
                4,
                ]],
                [name: 'cms-unit', 'shards': ['all']],
        ]
}

def buildParallelSteps() {
        def parallelSteps = [:]

        for (def suite in getSuites()) {
                def name = suite['name']

                for (def shard in suite['shards']) {
                        parallelSteps["${name}_${shard}"] = startTests(name, shard)
                }
        }

        return parallelSteps
}

stage('Prepare') {
        echo 'Starting the build...'
        slackSend channel: channel_name, color: 'good', message: "CI Tests started! ${env.JOB_NAME} (<${env.BUILD_URL}|Open>)", teamDomain: 'raccoongang', tokenCredentialId: 'slack-secret-token'
}

stage('Git Info') {
	node {
		checkout scm

		git_branch = env.BRANCH_NAME
		echo git_branch
		git_target = env.TARGET_BRANCH
		echo git_target
		git_commit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()

		if (git_branch != "ficus-rg") {
			// Determine actual PR commit, if necessary
			merge_commit_parents= sh(returnStdout: true, script: 'git rev-parse HEAD | git log --pretty=%P -n 1 --date-order').trim()
			if (merge_commit_parents.length() > 40) {
				echo 'More than one merge commit parent signifies that the merge commit is not the PR commit'
				echo "Changing git_commit from '${git_commit}' to '${merge_commit_parents.take(40)}'"
				git_commit = merge_commit_parents.take(40)
			} else {
				echo 'Only one merge commit parent signifies that the merge commit is also the PR commit'
				echo "Keeping git_commit as '${git_commit}'"
			}
		}
	}
}

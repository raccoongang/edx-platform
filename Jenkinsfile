#!groovy

def startTests(suite, shard) {
	return {
		echo "I am ${suite}:${shard}, and the worker is yet to be started!"

		node("${suite}-${shard}-worker") {
			context = "${suite}:${shard}"
			setBuildStatus ("${context}", 'Unit test', 'PENDING')
			
			cleanWs()

			checkout scm

			try {
				withEnv(["TEST_SUITE=${suite}", "SHARD=${shard}"]) {
					sh './scripts/all-tests.sh'
				}
			} catch (err) {
				setBuildStatus("${context}", 'Test failed :(', 'FAILURE')
				throw err
			} finally {
				archiveArtifacts 'reports/**, test_root/log/**'
				stash includes: 'reports/**, test_root/log/**', name: "artifacts-${suite}-${shard}"
				junit 'reports/**/*.xml'
			}
			
			setBuildStatus ("${context}", 'Test finished :)', 'SUCCESS')
			
			deleteDir()
		}
	}
}


def coverageTest() {
	node('coverage-report-worker') {
		context = "Coverage report"
		setBuildStatus ("${context}", 'Checking code coverage levels', 'PENDING')
		
		cleanWs()
		
		checkout scm

		try {
			unstash 'artifacts-lms-unit-1'
			unstash 'artifacts-lms-unit-2'
			unstash 'artifacts-lms-unit-3'
			unstash 'artifacts-lms-unit-4'
			unstash 'artifacts-cms-unit-all'
			withCredentials([string(credentialsId: '73037323-f1a4-44e2-8054-04d2a9580240', variable: 'CODE_COV_TOKEN')]) {
				CI_BRANCH = $(git rev-parse HEAD^1)                       
				TARGET_BRANCH = $(git rev-parse HEAD^2)  
				sh './scripts/jenkins-report.sh'
			}
		} catch (err) {
			setBuildStatus("${context}", 'Code coverage below 90%', 'FAILURE')
			throw err
		} finally {	
			archiveArtifacts 'reports/**, test_root/log/**'
			cobertura autoUpdateHealth: false, autoUpdateStability: false, coberturaReportFile: 'reports/coverage.xml', conditionalCoverageTargets: '70, 0, 0', failUnhealthy: false, failUnstable: false, lineCoverageTargets: '80, 0, 0', maxNumberOfBuilds: 0, methodCoverageTargets: '80, 0, 0', onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false
		}
		
		setBuildStatus ("${context}", 'Code coverage above 90%', 'SUCCESS')
		
		deleteDir()
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
}

stage('Unit tests') {
	parallel buildParallelSteps()
}

stage('Coverage') {
	coverageTest()
}

stage('Done') {
  echo 'Done! :)'
}

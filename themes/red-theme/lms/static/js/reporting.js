function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = cookies[i].trim();

			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}


function sendReports(){

	var csrftoken = getCookie('csrftoken');

	const exercitii = {};
	// exercitii ['nr_exercitii'] = exercises_count;

	for(i = 1; i <= exercises_count; i++){
		exercitii [`exercise_${i}`] = eval('exercise_' + i); 
	}

	console.log(exercitii); 


	const questions = Object.keys(exercitii).reduce((acc, exerciseName) => {

		const count = exercitii[exerciseName];

		return [...acc, {question_id: exerciseName, attempt_count: count}]
	}, [])

	const course = video_name;


	const url = '/api/video-lesson/';
	const token = 'Bearer 5c5d90ac4f731bb7e21ca64311cdd58abfa79c43';

	var new_json = { 
		course: course,
		video_id: video_id,
		questions: questions
	};
	const data = JSON.stringify(new_json);


	const xhr = new XMLHttpRequest();
	xhr.withCredentials = true;
	xhr.open("POST",url)

	xhr.addEventListener('readystatechange', function() {
		if (this.readyState === 4 && this.status == 200) {
			console.log(this.responseText);
		}
	})
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.setRequestHeader("Authorization",token);
	xhr.setRequestHeader("X-CSRFToken", csrftoken);
	xhr.send(data);
}

function disablePlaybar(){

	// disable playbar slider

	document.getElementsByClassName('playbarSliderThumb')[0].style.display = 'none'
	if (!cp.playbar.mainMovie._jumpToFrame) {
		cp.playbar.mainMovie._jumpToFrame = cp.playbar.mainMovie.jumpToFrame
		cp.playbar.mainMovie.jumpToFrame = function(a) {
			var stack = new Error().stack || ''
			var callerIsNotPlaybar =
			stack.indexOf('HTMLCanvasElement.moveSlider') == -1
			&& stack.indexOf('PlayBarSlider.moveSlider') == -1
			if (callerIsNotPlaybar) cp.playbar.mainMovie._jumpToFrame.call(cp.playbar.mainMovie, a)
		}
	}

}

function disablePlaybutton(){

	if (!document.getElementById("playButtons")) {
    
		var divPlayButtons = document.createElement("div");

	    divPlayButtons.id = "playButtons";
	    divPlayButtons.style.width = "150px";
	    divPlayButtons.style.height = "46px";
	    divPlayButtons.style.zIndex = '999';
	    divPlayButtons.style.position = 'relative';

	    document.getElementById("playbarBkGrnd").appendChild(divPlayButtons);

	}else{

		document.getElementById('playButtons').style.display = ''
	
	}
}

function enablePlaybutton(){

	document.getElementById('playButtons').style.display = 'none'

}
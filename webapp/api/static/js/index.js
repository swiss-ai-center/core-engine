"use strict";


axios.defaults.headers.post['Access-Control-Allow-Origin'] = '*';
const engineURL = "https://pi-engine.kube.isc.heia-fr.ch/"

let tasks = []
$( ".results" ).hide();

function faceAnalyze() {
	const url = `${engineURL}services/faceAnalyzer`
	const imagefile = document.querySelector('#image_analyze');

	axios.post(
		url,
		{ img: imagefile.files[0] },
		{
			headers: {
				"Content-Type": "multipart/form-data",
				accept: "application/json"
			},
		})
		.then((res) => { console.log("OK", res.data.jobId); tasks = [...tasks, {"jobId": res.data.jobId, "service": "FACE_ANALYZER"}] })
		.catch((err) => { console.log("NOK", err); })
		.finally(() => {
			console.log(tasks);
			updateTasksList();
		});
}


function detectFace() {
	const url = `${engineURL}services/faceDetection`;
	const imagefile = document.querySelector('#image_analyze');

	axios.post(
		url,
		{ image: imagefile.files[0] },
		{
			headers: {
				"Content-Type": "multipart/form-data",
				accept: "application/json"
			},
		})
		.then((res) => { console.log("OK", res.data.jobId); tasks = [...tasks, {"jobId": res.data.jobId, "service": "DETECT_FACE"}] })
		.catch((err) => { console.log("NOK", err); })
		.finally(() => {
			console.log(tasks);
			updateTasksList();
		});
}


function faceBlur() {
	const url = `${engineURL}services/faceBlur`
	const imagefile = document.querySelector('#image_analyze');

	axios.post(
		url,
		{ image: imagefile.files[0] },
		{
			headers: {
				"Content-Type": "multipart/form-data",
				accept: "application/json"
			},
		})
		.then((res) => { console.log("OK", res.data.jobId); tasks = [...tasks, {"jobId": res.data.jobId, "service": "FACE_BLUR"}] })
		.catch((err) => { console.log("NOK", err); })
		.finally(() => {
			console.log(tasks);
			updateTasksList();
		});
}


function showResults(jobId, service) {
	const url = `${engineURL}tasks/${jobId}`;

	$( ".results" ).prop( "disabled", true );
	$( ".results" ).hide();

	axios.get(url)
		.then((res) => {
			$('#box_result').val("").change();
			if (service === "FACE_ANALYZER") {
				$('#box_result').val(`${JSON.stringify(res.data, null, 4)}\n`).change();
				$('#box_result').show();
				$('#box_result').prop( "disabled", false );

			} else if (service === "FACE_BLUR") {
				axios.get(`${engineURL}tasks/${jobId}`)
					.then((res) => {
						$("#image_result").attr("src", res.data.blurred);
						$("#image_result").show()
						$('#image_result').prop( "disabled", false );
					})
			}
		})


	console.log(jobId)
}

function updateTasksList() {
	const tasksHTML = document.querySelector("#tasksList");
	tasksHTML.innerHTML = "";
	tasks.forEach(el => {
		tasksHTML.innerHTML += `<button class="button is-small" onclick="showResults(${el.jobId}, '${el.service}')"> ${el.jobId} </button>`
	})
}
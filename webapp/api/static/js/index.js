"use strict";


axios.defaults.headers.post['Access-Control-Allow-Origin'] = '*';
const engineURL = "https://pi-engine.kube.isc.heia-fr.ch/"

let tasks = []
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
	const resBox = document.querySelector("#box_result");
	const imgOutput = document.querySelector("#image_result");
	const imgContainer = document.querySelector("#img_results_container");
	const url = `${engineURL}tasks/${jobId}`;

	document.querySelectorAll(".results").forEach((el) => {
		console.log(el);
		el.style.visibility = "hidden";
	});

	axios.get(url)
		.then((res) => {
			resBox.value = "";
			imgContainer.disabled = true;
			if (service === "FACE_ANALYZER") {
				resBox.value = `${JSON.stringify(res.data, null, 4)}\n`;
				resBox.style.visibility = "visible";
			} else if (service === "FACE_BLUR") {
				axios.get(`${engineURL}tasks/${jobId}`)
					.then((res) => {
						imgOutput.src = res.data.blurred;
						imgOutput.style.visibility = "visible";
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
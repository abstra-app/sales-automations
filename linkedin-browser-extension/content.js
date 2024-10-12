require('dotenv').config();
console.log("extension live")
let lastUrl = null;

function isPersonPage() {
	const url = window.location.href;
	const user_profile_regex = /https:\/\/www\.linkedin\.com\/in\/[a-zA-Z0-9-]+/;
	return user_profile_regex.test(url);
}

function isCompanyPage() {
	const url = window.location.href;
	const company_profile_regex = /https:\/\/www\.linkedin\.com\/company\/[a-zA-Z0-9-]+/;
	return company_profile_regex.test(url);
}

function getPersonHandle() {
	const url = window.location.href;
	const user_profile_regex = /https:\/\/www\.linkedin\.com\/in\/([a-zA-Z0-9-]+)/;
	const match = url.match(user_profile_regex);
	return match[1];
}

function getCompanyHandle() {
	const url = window.location.href;
	const company_profile_regex = /https:\/\/www\.linkedin\.com\/company\/([a-zA-Z0-9-]+)/;
	const match = url.match(company_profile_regex);
	return match[1];
}

function getContent() {
	return Array.from(document.querySelectorAll("section"))
		.map(s => s.innerText)
		.join("\n"+(Array(100).fill("-").join(''))+"\n");
}

function getData() {
	if (isPersonPage()) {
		return {
			type: "person",
			content: getContent(),
			handle: getPersonHandle(),
			time: Date.now()
		};
	} else if (isCompanyPage()) {
		return {
			type: "company",
			content: getContent(),
			handle: getCompanyHandle(),
			time: Date.now()
		};
	}
}

function saveTime(data) {
	const key = data.type + ":" + data.handle;
	const value = data.time;
	localStorage.setItem(key, value);
}


async function send(data) {

	const lastTime = localStorage.getItem(data.type + ":" + data.handle);
	console.log("send( ) called")

	if (lastTime == null || lastTime < data.time - 1000*60*60*24) {

		for (let i = 0; i < 5; i++) {
			
			console.log("sending data");
      
      const fetch_url = process.env.APP_FETCH_URL;
			const response = await fetch(fetch_url, {
				method: "POST",
				body: JSON.stringify(data),
				headers: {
					"Content-Type": "application/json"
				}
			});
	
			const statusCode = response.status;
			console.log("statusCode:", statusCode);

			if (statusCode === 200) {
				console.log("Data sent successfully");
				saveTime(data);
				break;
			}

			else {
				console.log("Attempt", i+1, "failed");
				await new Promise(r => setTimeout (r, 1000));
			}
			
		}
	}
}

setInterval(async () => {

	const currentUrl = window.location.href;

	if (currentUrl !== lastUrl || lastUrl === null) {

		console.log("url changed");

		lastUrl = currentUrl;

		setTimeout(async () => {
			
			const data = getData();
			if (data) { await send(data); }
			
		}, 10000)

	}
}, 1000);

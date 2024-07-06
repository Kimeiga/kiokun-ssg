import { error } from '@sveltejs/kit';

export async function load({ params, fetch }) {
	const { word } = params;
	const filename = word.endsWith('.json') ? word : `${word}.json`;
	console.log(`Attempting to fetch /dictionary/${filename}`);
	try {
		const response = await fetch(`/dictionary/${filename}`);
		console.log(`Response status: ${response.status}`);
		if (!response.ok) {
			throw error(404, `Entry for ${word} not found`);
		}
		const entries = await response.json();
		console.log(`Entries: ${JSON.stringify(entries).slice(0, 100)}...`);
		return { entries };
	} catch (err) {
		console.error(`Error fetching ${filename}:`, err);
		throw error(404, `Entry for ${word} not found`);
	}
}

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { createReadStream } from 'fs';
import { createGunzip } from 'zlib';
import readline from 'readline';
import lzma from 'lzma-native';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const datasetsDir = path.join(__dirname, 'datasets');
let outputDir;

// Argument parsing (you may want to use a library like yargs for more robust parsing)
const args = process.argv.slice(2);
if (args.includes('--vercel')) {
	outputDir = path.join(__dirname, '..', '.vercel', 'output', 'static', 'dictionary');
} else if (args.includes('--build')) {
	outputDir = path.join(__dirname, '..', '.svelte-kit', 'output', 'client', 'dictionary');
} else {
	outputDir = path.join(__dirname, '..', 'dictionary');
}

console.log(`Output directory: ${outputDir}`);

console.log('Loading datasets...');

async function loadCompressedJson(filePath, isXz = false) {
	const fileStream = createReadStream(filePath);
	const decompressor = isXz ? lzma.createDecompressor() : createGunzip();
	const rl = readline.createInterface({
		input: fileStream.pipe(decompressor),
		crlfDelay: Infinity
	});

	const data = [];
	for await (const line of rl) {
		data.push(JSON.parse(line));
	}

	return data;
}
async function loadDataset(pattern) {
	console.log(`Searching for pattern: ${pattern}`);
	console.log(`In directory: ${datasetsDir}`);

	const files = await fs.readdir(datasetsDir);
	console.log(`Files in directory:`, files);

	const matchingFile = files.find((file) => {
		const match = file.match(pattern);
		console.log(`Checking file: ${file}, Match: ${match !== null}`);
		return match !== null;
	});

	if (!matchingFile) {
		throw new Error(`No ${pattern} file found in ${datasetsDir}`);
	}

	console.log(`Matched file: ${matchingFile}`);

	const filePath = path.join(datasetsDir, matchingFile);
	const ext = path.extname(filePath);

	if (ext === '.xz' || ext === '.gz') {
		if (matchingFile.includes('jsonl')) {
			return loadCompressedJson(filePath, ext === '.xz');
		} else {
			const decompressor = ext === '.xz' ? lzma.createDecompressor() : createGunzip();
			const content = await new Promise((resolve, reject) => {
				const chunks = [];
				createReadStream(filePath)
					.pipe(decompressor)
					.on('data', (chunk) => chunks.push(chunk))
					.on('end', () => resolve(Buffer.concat(chunks)))
					.on('error', reject);
			});
			return JSON.parse(content.toString());
		}
	} else {
		const content = await fs.readFile(filePath, 'utf-8');
		return JSON.parse(content);
	}
}

// Load all datasets
const jmdict_data = await loadDataset('jmdict-.*\\.json.*');
const jmnedict_data = await loadDataset('jmnedict-.*\\.json.*');
const kanjidic_data = await loadDataset('kanjidic2-.*\\.json.*');
const char_dict_data = await loadDataset('dictionary_char_.*\\.jsonl.*');
const word_dict_data = await loadDataset('dictionary_word_.*\\.jsonl.*');


console.log('All datasets loaded successfully.');

const data = {};
const word_index = {};
const jmdict_entries = {};

jmdict_data.words.forEach((entry, index) => {
	const keys = [];

	// Add all kanji representations
	entry.kanji?.forEach((kanji) => {
		keys.push(kanji.text);
		if (!word_index[kanji.text]) word_index[kanji.text] = { j: [] };
		word_index[kanji.text].j.push(index);
	});

	// Add all kana representations
	entry.kana?.forEach((kana) => {
		keys.push(kana.text);
		if (!word_index[kana.text]) word_index[kana.text] = { j: [] };
		word_index[kana.text].j.push(index);
	});

	// If no keys were found, skip this entry
	if (keys.length === 0) return;

	// Add the entry to each key
	keys.forEach((key) => {
		if (!data[key]) data[key] = [];
		data[key].push(entry);
	});

	// Clean and structure the entry
	jmdict_entries[index] = {
		...(entry.kanji && {
			k: entry.kanji.map((kanji) => ({
				...(kanji.common && { c: true }),
				...(kanji.text && { t: kanji.text }),
				...(kanji.tags.length && { g: kanji.tags })
			}))
		}),
		...(entry.kana && {
			r: entry.kana.map((kana) => ({
				...(kana.common && { c: true }),
				...(kana.text && { t: kana.text }),
				...(kana.tags.length && { g: kana.tags }),
				...(kana.appliesToKanji !== ['*'] && { a: kana.appliesToKanji }),
				...(kana.text && { r: kana.text }) // Note: jaconv.kata2alphabet is not available in JS
			}))
		}),
		...(entry.sense && {
			s: entry.sense.map((sense) => ({
				...(sense.antonym.length && { n: sense.antonym }),
				...(sense.appliesToKana !== ['*'] && { k: sense.appliesToKana }),
				...(sense.appliesToKanji !== ['*'] && { a: sense.appliesToKanji }),
				...(sense.dialect.length && { d: sense.dialect }),
				...(sense.field.length && { f: sense.field }),
				g:
					sense.gloss?.map((gloss) => ({
						...(gloss.gender && { g: gloss.gender }),
						...(gloss.type && { y: gloss.type }),
						...(gloss.text && { t: gloss.text })
					})) || [],
				...(sense.info.length && { i: sense.info }),
				...(sense.languageSource.length && { l: sense.languageSource }),
				...(sense.misc.length && { m: sense.misc }),
				...(sense.partOfSpeech.length && { p: sense.partOfSpeech }),
				...(sense.related.length && { r: sense.related })
			}))
		})
	};
});

// Ensure the output directory exists
await fs.mkdir(outputDir, { recursive: true });

console.log('Writing JSON files...');
let total_processed = 0;
for (const [key, entries] of Object.entries(data)) {
	await fs.writeFile(path.join(outputDir, `${key}.json`), JSON.stringify(entries), 'utf-8');
	total_processed++;
}

console.log(`Total processed entries: ${total_processed}`);
console.log(`Dictionary files have been written to: ${outputDir}`);

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { createGunzip } from 'zlib';
import JSONStream from 'JSONStream';

// Get the directory of the current module
const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Define paths relative to the script location
const INPUT_FILE = path.join(__dirname, 'jmdict-eng-3.5.0.json.gz');
const DEFAULT_OUTPUT_DIR = path.join(__dirname, "..", "dictionary");
const SVELTEKIT_OUTPUT_DIR = path.join(__dirname, "..", ".svelte-kit", "output", "client", "dictionary");
const VERCEL_OUTPUT_DIR = path.join(__dirname, "..", ".vercel", "output", "static", "dictionary");
const WRITE_CHUNK_SIZE = 1000; // Number of files to write at once

// Parse command line arguments
const args = process.argv.slice(2);
const isBuildMode = args.includes('-b') || args.includes('--build');
const isVercelMode = args.includes('-v') || args.includes('--vercel');

// Set the output directory based on the flags
let OUTPUT_DIR;
if (isVercelMode) {
    OUTPUT_DIR = VERCEL_OUTPUT_DIR;
} else if (isBuildMode) {
    OUTPUT_DIR = SVELTEKIT_OUTPUT_DIR;
} else {
    OUTPUT_DIR = DEFAULT_OUTPUT_DIR;
}
async function processJMdict() {
    console.log("Processing JMdict file...");
    console.log(`Input file: ${INPUT_FILE}`);
    console.log(`Output directory: ${OUTPUT_DIR}`);
    console.log(`Build mode: ${isBuildMode ? 'ON' : 'OFF'}`);

    const data = new Map();
    let processedCount = 0;

    await fs.promises.mkdir(OUTPUT_DIR, { recursive: true });

    const stream = fs.createReadStream(INPUT_FILE)
        .pipe(createGunzip())
        .pipe(JSONStream.parse('words.*'));

    await new Promise((resolve, reject) => {
        stream.on('data', (entry) => {
            const keys = [
                ...(entry.kanji || []).map(k => k.text),
                ...(entry.kana || []).map(k => k.text)
            ];

            for (const key of keys) {
                if (!data.has(key)) data.set(key, []);
                data.get(key).push(entry);
            }

            processedCount++;
            if (processedCount % 10000 === 0) {
                console.log(`Processed ${processedCount} entries`);
            }
        });

        stream.on('end', () => {
            console.log(`Total entries processed: ${processedCount}`);
            console.log(`Total unique keys: ${data.size}`);
            resolve();
        });

        stream.on('error', reject);
    });

    console.log("Writing files...");

    let writtenCount = 0;
    const entries = Array.from(data.entries());

    for (let i = 0; i < entries.length; i += WRITE_CHUNK_SIZE) {
        const chunk = entries.slice(i, i + WRITE_CHUNK_SIZE);
        await Promise.all(chunk.map(([key, entries]) => writeFile(key, entries)));
        writtenCount += chunk.length;
        console.log(`Written ${writtenCount} files`);
    }

    console.log("Processing complete.");
}

async function writeFile(key, entries) {
    const filePath = path.join(OUTPUT_DIR, `${key}.json`);
    await fs.promises.writeFile(filePath, JSON.stringify(entries), 'utf-8');
}

processJMdict().catch(console.error);
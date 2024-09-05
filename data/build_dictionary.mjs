import path from 'path';
import { fileURLToPath } from 'url';
// import { spawn } from 'child_process';
import { createReadStream, createWriteStream } from 'fs';
import { pipeline } from 'stream/promises';
import lzma from 'lzma-native';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const FILES_TO_UNZIP = [
    'jp/jmdict/jmdict-eng-3.5.0.json.xz',
    'jp/jmnedict/jmnedict-all-3.5.0.json.xz',
    'jp/kanjidic/kanjidic2-en-3.5.0.json.xz',
    'zh/char_dict/dictionary_char_2024-03-19.jsonl.xz',
    'zh/word_dict/dictionary_word_2024-03-19.jsonl.xz'
];

async function unzipFile(xzFilePath, outputFilePath) {
    const decompressor = lzma.createDecompressor();
    const inputStream = createReadStream(xzFilePath);
    const outputStream = createWriteStream(outputFilePath);

    await pipeline(inputStream, decompressor, outputStream);
}

// async function runPythonScript() {
//     return new Promise((resolve, reject) => {
//         const pythonProcess = spawn('python', ['-m', 'data.main'], {
//             env: {
//                 ...process.env,
//                 PYTHONPATH: path.resolve(__dirname, '..') // Add the parent directory to PYTHONPATH
//             }
//         });

//         pythonProcess.stdout.on('data', (data) => {
//             process.stdout.write(`Python script output: ${data}`);
//         });
        
//         pythonProcess.stderr.on('data', (data) => {
//             process.stderr.write(`Python script error: ${data}`);
//         });

//         pythonProcess.on('close', (code) => {
//             if (code === 0) {
//                 resolve();
//             } else {
//                 reject(new Error(`Python script exited with code ${code}`));
//             }
//         });
//     });
// }

async function buildDictionary() {
    console.log("Starting dictionary build process...");

    // Unzip files
    for (const file of FILES_TO_UNZIP) {
        const xzPath = path.join(__dirname, file);
        const outputPath = xzPath.replace('.xz', '');
        console.log(`Unzipping ${xzPath}...`);
        await unzipFile(xzPath, outputPath);
        console.log(`Finished unzipping ${xzPath}.`);
    }

    console.log("All files unzipped successfully.");

    // Run main.py with -m
    console.log("Running Python script using 'python -m data.main'...");
    // await runPythonScript();

    // console.log("Dictionary build process completed.");
}

buildDictionary().catch(console.error);

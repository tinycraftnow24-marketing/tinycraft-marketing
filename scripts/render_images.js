const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const IMAGES_DIR = path.join(__dirname, '..', 'images');

async function renderHtmlToPng(htmlPath, outputPath, width, height) {
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width, height, deviceScaleFactor: 2 });
  const fileUrl = 'file://' + htmlPath.replace(/\\/g, '/');
  await page.goto(fileUrl, { waitUntil: 'networkidle0' });
  await page.screenshot({ path: outputPath, fullPage: false });
  await browser.close();
  console.log(`Rendered: ${path.basename(outputPath)}`);
}

async function main() {
  const entries = fs.readdirSync(IMAGES_DIR, { withFileTypes: true });
  const productDirs = entries
    .filter(e => e.isDirectory() && e.name !== 'collection')
    .map(e => e.name);

  for (const product of productDirs) {
    const dir = path.join(IMAGES_DIR, product);

    const pinterestHtml = path.join(dir, 'editorial-pinterest.html');
    const pinterestPng  = path.join(dir, 'editorial-pinterest.png');
    if (fs.existsSync(pinterestHtml) && !fs.existsSync(pinterestPng)) {
      await renderHtmlToPng(pinterestHtml, pinterestPng, 1000, 1500);
    }

    const thumbHtml = path.join(dir, 'thumbnail.html');
    const thumbPng  = path.join(dir, 'thumbnail.png');
    if (fs.existsSync(thumbHtml) && !fs.existsSync(thumbPng)) {
      await renderHtmlToPng(thumbHtml, thumbPng, 600, 600);
    }
  }

  const collectionHtml = path.join(IMAGES_DIR, 'collection', 'collection.html');
  const collectionPng  = path.join(IMAGES_DIR, 'collection', 'collection.png');
  if (fs.existsSync(collectionHtml) && !fs.existsSync(collectionPng)) {
    await renderHtmlToPng(collectionHtml, collectionPng, 1000, 1500);
  }
}

main().catch(err => { console.error(err); process.exit(1); });

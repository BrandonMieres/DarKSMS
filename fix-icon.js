const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  const icoPath = path.resolve('public/icono.ico');
  const icoBase64 = fs.readFileSync(icoPath).toString('base64');
  const html = `
    <html>
    <body style="margin: 0; background: transparent;">
      <canvas id="c" width="256" height="256"></canvas>
      <script>
        const img = new Image();
        img.onload = () => {
          const ctx = document.getElementById('c').getContext('2d');
          ctx.imageSmoothingEnabled = true;
          ctx.imageSmoothingQuality = 'high';
          ctx.drawImage(img, 0, 0, 256, 256);
          window.ready = true;
        };
        img.src = 'data:image/x-icon;base64,${icoBase64}';
      </script>
    </body>
    </html>
  `;
  await page.setContent(html);
  await page.waitForFunction('window.ready === true');
  
  const dataUrl = await page.evaluate(() => {
    return document.getElementById('c').toDataURL('image/png');
  });
  
  const base64Data = dataUrl.replace(/^data:image\/png;base64,/, "");
  fs.writeFileSync('build/icon.png', base64Data, 'base64');
  console.log('Saved 256x256 icon to build/icon.png');
  
  await browser.close();
})();

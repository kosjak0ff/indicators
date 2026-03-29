const { spawn } = require("child_process");
const fs = require("fs");
const http = require("http");
const os = require("os");
const path = require("path");
const { accessSync, constants } = require("fs");

const CHROME_CANDIDATES = [
  process.env.CHROME_BIN,
  "google-chrome-stable",
  "google-chrome",
  "chromium",
  "chromium-browser",
  "chrome",
].filter(Boolean);

function isExecutable(filePath) {
  try {
    accessSync(filePath, constants.X_OK);
    return true;
  } catch {
    return false;
  }
}

function findExecutable(binary) {
  if (binary.includes(path.sep)) {
    return isExecutable(binary) ? binary : null;
  }

  const searchPath = process.env.PATH || "";
  for (const directory of searchPath.split(path.delimiter)) {
    if (!directory) {
      continue;
    }

    const candidatePath = path.join(directory, binary);
    if (isExecutable(candidatePath)) {
      return candidatePath;
    }
  }

  return null;
}

function resolveChromeBinary() {
  for (const candidate of CHROME_CANDIDATES) {
    const resolved = findExecutable(candidate);
    if (resolved) {
      return resolved;
    }
  }

  throw new Error(
    `Could not find a Chrome/Chromium binary. Tried: ${CHROME_CANDIDATES.join(", ")}. ` +
      "Install one of them or set CHROME_BIN to the browser path."
  );
}

function getJson(url) {
  return new Promise((resolve, reject) => {
    http
      .get(url, (res) => {
        let data = "";
        res.on("data", (chunk) => {
          data += chunk;
        });
        res.on("end", () => {
          try {
            resolve(JSON.parse(data));
          } catch (error) {
            reject(new Error(`Invalid JSON from ${url}: ${data.slice(0, 200)}`));
          }
        });
      })
      .on("error", reject);
  });
}

async function main() {
  const url = process.argv[2];
  if (!url) {
    throw new Error("Usage: node scripts/render_page_text.js <url>");
  }

  const userDataDir = fs.mkdtempSync(path.join(os.tmpdir(), "cg-render-"));
  const chromeBinary = resolveChromeBinary();
  const chrome = spawn(
    chromeBinary,
    [
      "--headless=new",
      "--no-sandbox",
      "--disable-gpu",
      "--disable-dev-shm-usage",
      "--disable-blink-features=AutomationControlled",
      "--remote-debugging-port=9222",
      `--user-data-dir=${userDataDir}`,
      "about:blank",
    ],
    { stdio: ["ignore", "ignore", "pipe"] }
  );

  let chromeStderr = "";
  chrome.stderr.on("data", (chunk) => {
    chromeStderr += chunk.toString();
  });

  const cleanup = () => {
    try {
      chrome.kill("SIGKILL");
    } catch {
      // Ignore cleanup failures.
    }
  };

  try {
    await new Promise((resolve) => setTimeout(resolve, 1500));
    const targets = await getJson("http://127.0.0.1:9222/json/list");
    const page = targets.find((target) => target.type === "page");
    if (!page) {
      throw new Error(`No Chrome page target found. stderr: ${chromeStderr}`);
    }

    const ws = new WebSocket(page.webSocketDebuggerUrl);
    let requestId = 0;
    const pending = new Map();

    function send(method, params = {}) {
      const id = ++requestId;
      ws.send(JSON.stringify({ id, method, params }));
      return new Promise((resolve, reject) => {
        pending.set(id, { resolve, reject });
      });
    }

    ws.onmessage = ({ data }) => {
      const message = JSON.parse(data.toString());
      if (!message.id || !pending.has(message.id)) {
        return;
      }

      const { resolve, reject } = pending.get(message.id);
      pending.delete(message.id);

      if (message.error) {
        reject(new Error(JSON.stringify(message.error)));
        return;
      }

      resolve(message.result);
    };

    await new Promise((resolve) => {
      ws.onopen = resolve;
    });

    await send("Page.enable");
    await send("Runtime.enable");
    await send("Network.enable");
    await send("Emulation.setUserAgentOverride", {
      userAgent:
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
      acceptLanguage: "en-US,en;q=0.9",
      platform: "Linux x86_64",
    });
    await send("Page.navigate", { url });
    await new Promise((resolve) => setTimeout(resolve, 12000));

    const result = await send("Runtime.evaluate", {
      expression: `(() => ({
        title: document.title,
        text: document.body ? document.body.innerText : ""
      }))()`,
      returnByValue: true,
    });

    process.stdout.write(JSON.stringify(result.result.value));
    ws.close();
  } finally {
    cleanup();
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});

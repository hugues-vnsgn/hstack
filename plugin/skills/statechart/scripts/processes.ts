import { type ChildProcess, spawn } from "node:child_process";

type Processes = {
  killTree: (pid: number) => Promise<unknown>;
  startJanitor: (job: { pid: number | undefined; folders: [string, string] }) => ChildProcess;
};

const posix: Processes = {
  killTree: (pid) =>
    new Promise((resolve) =>
      spawn("/bin/sh", ["-c", 'kill -s KILL -- "-$1"', "sh", String(pid)], { stdio: "ignore" }).on(
        "exit",
        resolve,
      ),
    ),
  startJanitor: ({ pid, folders }) =>
    spawn(
      "/bin/sh",
      [
        "-c",
        'while read -r line; do :; done; kill -s KILL -- "-$1"; rm -rf -- "$2" "$3"',
        "sh",
        String(pid),
        ...folders,
      ],
      { detached: true, stdio: ["pipe", "ignore", "ignore"] },
    ),
};

const WINDOWS_KILL_TREE = `const run = (file, args) =>
  require("node:child_process").spawnSync(file, args, { encoding: "utf8", windowsHide: true }).stdout;
const listed = (pid) =>
  run("tasklist", ["/NH", "/FO", "CSV", "/FI", "PID eq " + pid]).includes(JSON.stringify(pid));
async function killTree(pid) {
  const lines = run("taskkill", ["/T", "/F", "/PID", pid]).split("\\n");
  const killed = lines.map((line) => line.match(/\\d+/)?.[0]).filter((id) => id);
  for (const end = Date.now() + 60_000; killed.some(listed) && Date.now() < end; )
    await new Promise((resolve) => setTimeout(resolve, 100));
}`;

const win32: Processes = {
  killTree: (pid) =>
    new Promise((resolve) =>
      spawn(
        process.execPath,
        ["-e", `${WINDOWS_KILL_TREE}\nkillTree(process.argv[1]);`, String(pid)],
        { stdio: "ignore", windowsHide: true },
      ).on("exit", resolve),
    ),
  startJanitor: ({ pid, folders }) =>
    spawn(
      process.execPath,
      [
        "-e",
        `${WINDOWS_KILL_TREE}
const [pid, ...folders] = process.argv.slice(1);
process.stdin.on("end", async () => {
  await killTree(pid);
  for (const folder of folders) require("node:fs").rmSync(folder, { recursive: true, force: true });
}).resume();`,
        String(pid),
        ...folders,
      ],
      { detached: true, stdio: ["pipe", "ignore", "ignore"] },
    ),
};

export const { killTree, startJanitor } = process.platform === "win32" ? win32 : posix;

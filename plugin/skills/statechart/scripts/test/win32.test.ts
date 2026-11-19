import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { once } from "node:events";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { test } from "node:test";
import { setTimeout as sleep } from "node:timers/promises";
import { killTree, startJanitor } from "../processes.ts";

const skip = process.platform !== "win32" && "the win32 process seam runs only on Windows";

const alive = (pid: number) => {
  try {
    process.kill(pid, 0);
    return true;
  } catch (error) {
    assert.ok(error instanceof Error && "code" in error && error.code === "ESRCH", String(error));
    return false;
  }
};

async function assertGone(pid: number) {
  for (let i = 0; alive(pid); i++) {
    assert.ok(i < 250, `Process ${pid} is still running.`);
    await sleep(20);
  }
}

async function startTree(dir: string) {
  const pids = path.join(dir, "pids");
  const hold = (name: string) =>
    `require("node:fs").openSync(${JSON.stringify(path.join(dir, name))}, "w");` +
    `setInterval(() => {}, 1000);`;
  spawn(
    process.execPath,
    [
      "-e",
      `const fs = require("node:fs");` +
        `const grandchild = require("node:child_process").spawn(process.execPath, ["-e", ${JSON.stringify(hold("grandchild"))}], { stdio: "ignore" });` +
        `fs.writeFileSync(${JSON.stringify(`${pids}.part`)}, process.pid + " " + grandchild.pid);` +
        `fs.renameSync(${JSON.stringify(`${pids}.part`)}, ${JSON.stringify(pids)});` +
        hold("child"),
    ],
    { detached: true, stdio: "ignore" },
  ).unref();
  for (let i = 0; !fs.existsSync(pids); i++) {
    assert.ok(i < 250, "The process tree did not start.");
    await sleep(20);
  }
  const [child, grandchild] = fs.readFileSync(pids, "utf8").split(" ").map(Number);
  assert.ok(alive(child) && alive(grandchild));
  return { child, grandchild };
}

test("killTree stops a detached process and the process it started", { skip }, async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "statechart-win32-"));
  const { child, grandchild } = await startTree(dir);
  await killTree(child);
  await assertGone(child);
  await assertGone(grandchild);
  fs.rmSync(dir, { recursive: true });
});

test(
  "the janitor waits for its stdin to close, then stops the tree and removes the folders",
  { skip, timeout: 30_000 },
  async () => {
    const stage = fs.mkdtempSync(path.join(os.tmpdir(), "statechart-win32-stage-"));
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "statechart-win32-tmp-"));
    const { child, grandchild } = await startTree(tmp);
    fs.writeFileSync(path.join(stage, "draft"), "");
    const janitor = startJanitor({ pid: child, folders: [stage, tmp] });
    const exited = once(janitor, "exit");
    await sleep(500);
    assert.ok(alive(child) && alive(grandchild));
    assert.ok(fs.existsSync(stage) && fs.existsSync(tmp));
    assert.ok(janitor.stdin);
    janitor.stdin.end();
    const [code] = await exited;
    assert.equal(code, 0);
    await assertGone(child);
    await assertGone(grandchild);
    assert.equal(fs.existsSync(stage), false);
    assert.equal(fs.existsSync(tmp), false);
  },
);

import fs from "node:fs";

const list = text => text === "none" ? [] : (text ?? "").split(",").map(s => s.trim()).filter(Boolean);
const meaningful = text => {
	const value = text?.replace(/[\u200b-\u200d\ufeff]/g, "").trim();
	return Boolean(value) && !/^<[^>]*>$|<(?:[a-z_][a-z0-9_-]*|)>/i.test(value) && !/^(none|unknown|unresolved|tbd|n\/a)$/i.test(value);
};

export function validateCoverage(pr, coverage, live, fail) {
	const catalog = JSON.parse(fs.readFileSync(new URL("../references/mobile-risks.json", import.meta.url), "utf8"));
	const reject = (n, message) => fail(n ?? pr.n, `${pr.title}: ${message}`);
	const fields = new Map(), targets = new Map(), risks = new Map();
	for (const line of coverage?.lines.filter(l => !l.code && l.text.trim()) ?? []) {
		let match = line.text.match(/^- Target ([a-z0-9-]+)\. Platform (android|ios)\. Identity (.+)\.$/);
		if (match) {
			if (targets.has(match[1]) || !meaningful(match[3])) reject(line.n, "duplicate or invalid target");
			targets.set(match[1], {platform: match[2], identity: match[3]});
			continue;
		}
		match = line.text.match(/^- Risk ([a-z-]+)\. (applicable|not-applicable|unresolved)\. Checks (.+?)\. Reason (.+)\.$/);
		if (match) {
			const [reason, approval] = match[4].split(". Approval ");
			if (risks.has(match[1]) || !meaningful(reason)) reject(line.n, "duplicate or invalid risk reason");
			if (match[2] === "unresolved") reject(line.n, `unresolved risk ${match[1]}`);
			if (match[2] === "not-applicable" && (!meaningful(approval) || match[3] !== "none")) reject(line.n, `risk ${match[1]} needs an exemption reason/approval and no checks`);
			risks.set(match[1], {status: match[2], checks: list(match[3]), n: line.n});
			continue;
		}
		match = line.text.match(/^- (Work type|Platforms|Areas|Source|Live|Performance)\. (.+)\.$/);
		if (!match || fields.has(match[1])) reject(line.n, "unknown or duplicate coverage field");
		else fields.set(match[1], match[2]);
	}
	for (const name of ["Work type", "Platforms", "Areas", "Source", "Live", "Performance"]) {
		if (!fields.has(name)) reject(coverage?.n, `missing coverage field ${name}`);
	}
	if (!meaningful(fields.get("Source"))) reject(coverage?.n, "missing source/diff evidence");
	const workType = fields.get("Work type");
	const behavior = workType === "mobile-behavior";
	if (!["mobile-behavior", "documentation", "tooling-workflow"].includes(workType)) reject(coverage?.n, "unknown work type");
	const applicability = name => {
		const value = fields.get(name) ?? "";
		if (value === "applicable") return true;
		const match = value.match(/^not-applicable\. Reason (.+)\. Approval (.+)$/);
		if (!match || !meaningful(match[1]) || !meaningful(match[2])) reject(coverage?.n, `${name} needs applicability or exemption reason/approval`);
		return false;
	};
	const liveApplies = applicability("Live"), perfApplies = applicability("Performance");
	if (behavior && !liveApplies) reject(coverage?.n, "mobile behavior requires live proof");
	if (!behavior && (liveApplies || perfApplies)) reject(coverage?.n, "documentation needs explicit non-applicability");
	const platforms = list(fields.get("Platforms"));
	if ((behavior && !platforms.length) || new Set(platforms).size !== platforms.length || platforms.some(p => !["android", "ios"].includes(p))) reject(coverage?.n, "invalid affected platforms");
	if (!behavior && (fields.get("Platforms") !== "none" || targets.size)) reject(coverage?.n, "documentation cannot declare mobile targets");
	for (const platform of platforms) {
		if (![...targets.values()].some(t => t.platform === platform)) reject(coverage?.n, `missing ${platform} target`);
	}
	for (const [id, target] of targets) {
		if (!platforms.includes(target.platform)) reject(coverage?.n, `target ${id} uses undeclared platform`);
	}
	const areas = list(fields.get("Areas"));
	const required = new Set();
	if (!areas.length || new Set(areas).size !== areas.length) reject(coverage?.n, "invalid changed areas");
	if (!behavior && fields.get("Areas") !== (workType === "documentation" ? "documentation" : "workflow")) reject(coverage?.n, "work type must match its changed area");
	if (behavior && areas.some(a => ["documentation", "workflow"].includes(a))) reject(coverage?.n, "mobile behavior needs mobile changed areas");
	for (const area of areas) {
		if (!Object.hasOwn(catalog, area)) {
			reject(coverage?.n, `unknown changed area ${area}`);
			continue;
		}
		for (const risk of catalog[area]) required.add(risk);
	}
	for (const risk of required) if (!risks.has(risk)) reject(coverage?.n, `missing risk ${risk}`);
	for (const risk of risks.keys()) if (!required.has(risk)) reject(coverage?.n, `undeclared risk ${risk}`);
	const checks = new Map();
	for (const line of live?.lines.filter(l => !l.code && /^\s*- \[[ x]\]/.test(l.text)) ?? []) {
		const definition = line.text.replace(/(?: Evidence\.)?(?: \[(?:Run|Screenshot|Video|Log|Trace|Receipt)\]\([^)]*\))+\s*$/, "");
		const match = definition.match(/^- \[[ x]\] Lane ([1-9][0-9]*)\. (.+?) Risks `([^`]+)`\. Target `([^`]+)`\. Reason (.+?)\. Action (.+?)\. Save `([^`]+)`\. Pass when (.+)\.$/);
		if (!match) {
			reject(line.n, "live check needs scenario, risks, target, reason, action, artifact and pass condition");
			continue;
		}
		for (const [i, field] of [[2, "scenario"], [5, "reason"], [6, "action"], [7, "artifact"], [8, "pass condition"]]) {
			if (!meaningful(match[i])) reject(line.n, `check ${match[1]} has an unresolved ${field}`);
		}
		const [id, tagged, target] = [match[1], list(match[3]), match[4]];
		if (checks.has(id)) reject(line.n, `duplicate check ${id}`);
		if (!targets.has(target)) reject(line.n, `check ${id} uses unknown target ${target}`);
		if (!tagged.length || new Set(tagged).size !== tagged.length) reject(line.n, `check ${id} has invalid risks`);
		for (const risk of tagged) if (risks.get(risk)?.status !== "applicable") reject(line.n, `check ${id} uses undeclared/exempt risk ${risk}`);
		for (const risk of tagged) if (!risks.get(risk)?.checks.includes(id)) reject(line.n, `check ${id} has inconsistent risk mapping for ${risk}`);
		checks.set(id, {id, target, risks: tagged, action: match[6], expected: match[8], artifact: match[7]});
	}
	for (const [risk, row] of risks) {
		if (row.status !== "applicable") continue;
		if (new Set(row.checks).size !== row.checks.length) reject(row.n, `risk ${risk} has duplicate check IDs`);
		for (const id of row.checks) if (!checks.get(id)?.risks.includes(risk)) reject(row.n, `risk ${risk} references missing or mismatched check ${id}`);
		for (const target of targets.keys()) {
			if (!row.checks.some(id => checks.get(id)?.target === target && checks.get(id)?.risks.includes(risk))) reject(row.n, `risk ${risk} has no check on ${target}`);
		}
	}
	return {live: liveApplies, perf: perfApplies, workType, checks: [...checks.values()]};
}

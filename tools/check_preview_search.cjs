// Exercise the search worker shipped by MkDocs Material in the 1.4 build.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

async function check(site) {
  const directory = path.join(site, "assets/javascripts/workers");
  const workers = fs.readdirSync(directory).filter(name => /^search\..+\.min\.js$/.test(name));
  assert.equal(workers.length, 1, "expected one generated Material search worker");
  const index = JSON.parse(fs.readFileSync(path.join(site, "search/search_index.json"), "utf8"));
  const locations = new Set();
  for (const {location} of index.docs) {
    const route = location.split("#", 1)[0];
    assert.match(route, /^(?:[\w-]+\/)*$/, location);
    assert(fs.existsSync(path.join(site, route, "index.html")), "search result has no preview page: " + location);
    locations.add(route);
  }
  assert(locations.has(""), "the preview home is missing from search");
  assert(!locations.has("quickstart/"), "the shared 1.3 quickstart leaked into 1.4 search");

  let receive;
  let response;
  const worker = {
    console: {warn(error) { throw new Error(error); }},
    addEventListener(type, callback) {
      assert.equal(type, "message");
      receive = callback;
    },
    postMessage(message) { response = message; },
  };
  worker.self = worker;
  vm.runInNewContext(fs.readFileSync(path.join(directory, workers[0]), "utf8"), worker);
  await receive({data: {type: 0, data: {...index, options: {suggest: true}}}});
  assert.equal(response.type, 1);

  const expected = {
    "result_format": "result-files/#result_format",
    "workflow.status": "calculation-logs/#termination-status",
    "32 vcpu": "installation/#concurrent-compute-budget",
  };
  for (const [query, target] of Object.entries(expected)) {
    await receive({data: {type: 2, data: query}});
    assert.equal(response.type, 3);
    const matches = response.data.items.flat().map(item => item.location);
    assert(matches.includes(target), query + " did not return " + target);
    console.log(query + " → " + target);
  }
}

check(process.argv[2]).catch(error => {
  console.error(error);
  process.exitCode = 1;
});

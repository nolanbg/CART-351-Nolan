// Front end for The Daily Panderer

let swarms = [];
let revealed = false;
let hoveredNode = null;
let projection, land;

const VOICE_COLORS = {
  outraged: [230, 60, 60],
  concerned: [240, 170, 40],
  cheerful: [70, 190, 120],
  sloppy: [120, 140, 230],
};

// ---------- map ----------

// Needs width/height, so call after createCanvas and again on resize.
function buildProjection() {
  projection = d3.geoEquirectangular().fitSize([width, height], { type: "Sphere" });
}

// Runs once: fetches the file and converts it. 
async function loadMap() {
  try {
    const res = await fetch("/static/land-110.json"); 
    if (!res.ok) throw new Error("Map file not found: " + res.status);
    const world = await res.json();
    land = topojson.feature(world, world.objects.land);
  } catch (err) {
    console.error("Map failed to load, continuing without it:", err);
    
  }
  
}

function drawMap() {
  if (!land || !projection) return;
  const dark = document.body.classList.contains("theme-alarm");
  const ctx = drawingContext;
  ctx.save();
  ctx.beginPath();
  d3.geoPath(projection, ctx)(land);
  ctx.fillStyle = "red";
  ctx.fill();
  ctx.restore();
}

// d3 wants [lon, lat], so the order is flipped on purpose.
function project(lat, lon) {
  if (!projection) return { x: width / 2, y: height / 2 };
  const [x, y] = projection([lon, lat]);
  return { x, y };
}

// ---------- p5 lifecycle ----------

async function setup() {
  const holder = document.getElementById("canvas-holder");
  holder.style.height = "calc(100vh - 230px)";
  const c = createCanvas(holder.clientWidth, holder.clientHeight);
  c.parent(holder);
  textFont("monospace");

  document.getElementById("send").addEventListener("click", sendClaim);
  document.getElementById("reveal").addEventListener("click", () => (revealed = !revealed));
  document.getElementById("reset").addEventListener("click", resetAll);
  document.getElementById("claim").addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendClaim();
  });

  buildProjection();     // needs the canvas size
  await loadMap();       // sets `land`
  await loadSwarms();    // only now build nodes, so project() works
  console.log("projection:", !!projection, "canvas:", width, height);
}

function draw() {
  const dark = document.body.classList.contains("theme-alarm");
  background(dark ? 10 : 244);
  drawMap();

  hoveredNode = null;

  for (const swarm of swarms) {
    if (revealed) drawSpokes(swarm);

    for (const n of swarm.nodes) {
      if (millis() < n.visibleAt) continue;
      n.x = lerp(n.x, n.tx, 0.08);
      n.y = lerp(n.y, n.ty, 0.08);
      drawNode(n);
      if (dist(mouseX, mouseY, n.x, n.y) < n.r + 3) hoveredNode = n;
    }
  }

  updateTooltip();
  updateTrendCounter();
}

function windowResized() {
  const holder = document.getElementById("canvas-holder");
  resizeCanvas(holder.clientWidth, holder.clientHeight);
  buildProjection();
  loadSwarms();          // rebuild nodes so positions match the new size
}

// ---------- drawing helpers ----------

function drawNode(n) {
  const isHumanRevealed = revealed && n.isOriginal;
  const col = isHumanRevealed ? [255, 255, 255] : VOICE_COLORS[n.voice] || [200, 200, 200];
  noStroke();
  fill(col[0], col[1], col[2], 200);
  circle(n.x, n.y, isHumanRevealed ? n.r * 3 : n.r * 2);
  // TODO: pulse newly-arrived nodes 
}

function drawSpokes(swarm) {
  const origin = swarm.nodes[0];
  stroke(255, 40);
  for (const n of swarm.nodes.slice(1)) {
    if (millis() >= n.visibleAt) line(origin.x, origin.y, n.x, n.y);
  }
}

// ---------- building swarm objects from server data ----------

function buildSwarm(data, index, animate) {
  const now = millis();

  // Origin: the original post's own lat/lon, else a fallback (Montréal).
  const originPos = (data.original.lat !== undefined)
    ? project(data.original.lat, data.original.lon)
    : project(45.5, -73.6);

  const makeNode = (src, isOriginal, delay) => {
    const p = (src.lat !== undefined) ? project(src.lat, src.lon) : originPos;
    return {
      handle: src.handle,
      text: src.text,
      voice: src.voice,
      mutations: src.mutations || [],
      isOriginal,
      r: isOriginal ? 5 : 4,
      x: originPos.x, y: originPos.y,          // everyone spawns at the origin...
      tx: p.x + random(-4, 4),                 // ...and travels to its own spot (small jitter)
      ty: p.y + random(-4, 4),
      visibleAt: animate ? now + delay : 0,
    };
  };

  const nodes = [makeNode(data.original, true, 0)];
  for (const b of data.bots) nodes.push(makeNode(b, false, b.delay_ms));
  return { id: data.id, nodes };
}

// ---------- fetch calls ----------

// GET: load every saved swarm for the collective view.
async function loadSwarms() {
  try {
    const res = await fetch("/api/swarms");
    const data = await res.json();
    swarms = data.swarms.map((s, i) => buildSwarm(s, i, false));
  } catch (err) {
    console.error("Could not load swarms:", err);
  }
}

// POST: send one claim, get the whole swarm back, animate it in.
async function sendClaim() {
  const input = document.getElementById("claim");
  const text = input.value.trim();
  if (!text) return;

  try {
    const res = await fetch("/api/amplify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) {
      const err = await res.json();
      alert(err.error || "Something went wrong.");
      return;
    }
    const swarm = await res.json();
    swarms.push(buildSwarm(swarm, swarms.length, true));
    input.value = "";
  } catch (err) {
    console.error("Amplify failed:", err);
  }
}

async function resetAll() {
  await fetch("/api/reset", { method: "POST" });
  revealed = false;
  loadSwarms();
}

// ---------- UI text ----------

function updateTooltip() {
  const tip = document.getElementById("tooltip");
  if (!hoveredNode) { tip.style.display = "none"; return; }
  tip.style.display = "block";
  const rect = document.getElementById("canvas-holder").getBoundingClientRect();
  tip.style.left = rect.left + mouseX + 15 + "px";
  tip.style.top = rect.top + window.scrollY + mouseY + 15 + "px";
  tip.textContent = `@${hoveredNode.handle}: ${hoveredNode.text}`;
}

function updateTrendCounter() {
  if (swarms.length === 0) return;
  const latest = swarms[swarms.length - 1];
  const visible = latest.nodes.filter((n) => millis() >= n.visibleAt).length;
  document.getElementById("trend").textContent = `TRENDING · ${visible} posts`;
}
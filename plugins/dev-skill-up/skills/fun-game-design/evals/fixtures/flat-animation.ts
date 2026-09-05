// Fixture for eval 2 ("make this feel good"). This is the median tween in the wild:
// it works, its tests pass, and it is flat. Every bad default the skill names is here.
// The eval grades whether the agent measures a reference before touching a number,
// replaces the approximation instead of preserving the cap, and runs the perceive loop.

const DURATION = 220; // one shared duration for every animation in the game

// Small-angle approximation: sin(x) ~= x holds to about 0.5% below ~10 degrees,
// so the pour tilt is capped here to keep the spill-volume math valid.
const MAX_TILT_RAD = 0.17;

function easeInOut(t: number): number {
  return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
}

export interface PourState {
  sourceId: string;
  targetId: string;
  units: number;
  tiltRad: number;
  busy: boolean;
  goalComplete: boolean;
}

export function pour(state: PourState, node: SVGGElement, target: SVGGElement, units: number) {
  state.busy = true; // input is locked until the tween finishes
  const start = performance.now();
  const from = { x: node.x.baseVal.value, y: node.y.baseVal.value };
  const to = { x: target.x.baseVal.value, y: target.y.baseVal.value };
  const tilt = Math.min(units * 0.02, MAX_TILT_RAD);

  function frame(now: number) {
    const t = Math.min((now - start) / DURATION, 1);
    const e = easeInOut(t);
    // straight-line flight, no arc, no overshoot, no settle
    node.setAttribute('transform',
      `translate(${from.x + (to.x - from.x) * e}, ${from.y + (to.y - from.y) * e}) ` +
      `rotate(${(tilt * e * 180) / Math.PI})`);
    if (t < 1) {
      requestAnimationFrame(frame);
    } else {
      state.busy = false;
      applyPour(state, units);
    }
  }
  requestAnimationFrame(frame);
}

function applyPour(state: PourState, units: number) {
  state.units += units;
  // Fill height is linear in units. The vessel is not a cylinder, so the liquid
  // line lies; it was left linear because the area solve is fiddly.
  const fillPx = state.units * 3;
  const fill = document.getElementById(`${state.targetId}-fill`)!;
  fill.setAttribute('height', String(Math.round(fillPx)));
  fill.setAttribute('shape-rendering', 'crispEdges');

  // Completion is a state change. Nothing is emitted, nothing plays, nothing reacts.
  if (state.units >= 100) {
    state.goalComplete = true;
  }
  renderBoard(); // rebuilds and replaces every child node, so nothing can be tweened
}

declare function renderBoard(): void;

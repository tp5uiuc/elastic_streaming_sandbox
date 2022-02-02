/* Initialization functions*/

class ScriptLoader {
    constructor(script) {
        this.script = script;
        this.scriptElement = document.createElement("script");
        this.head = document.querySelector("head");
    }

    load() {
        return new Promise((resolve, reject) => {
            this.scriptElement.src = this.script;
            this.scriptElement.onload = e => resolve(e);
            this.scriptElement.onerror = e => reject(e);
            this.head.appendChild(this.scriptElement);
        });
    }
}


// async function to fetch the raw content of the gist
/**
 * @param filename
 */
async function fetchFile(filename) {

    // const gistID = 'ea4b6c8e831ff923640aeda185241d14'
    // const url = `https://api.github.com/gists/${gistID}`
    // const fileName = "random_walk_2d.py"

    const rawContent = await fetch(filename)

    // .then(res => res.json())
        .then(data =>

        // console.log(data.text());
            data.text()

            // return data.files[fileName].content;
        );

    // console.log(rawContent);

    return rawContent;
}


class RigidDefaultParams {
  static defaultWomersley() {
    // -1 because slider starts at 1
    return 8 * 10; //scaling
  }
  static defaultCau() {
    return 0; // scaling
  }
  static defaultZeta() {
    return 0.2 * 10; // scaling
  }
}

class ElasticDefaultParams {
  static defaultWomersley() {
    // -1 because slider starts at 1
    return 8 * 10;
  }
  static defaultCau() {
    return 0.05 * 100;
  }
  static defaultZeta() {
    return 0.2 * 10;
  }
}

class PlotRange{
  static radius(){
    return 1.0;
  }
  static min(){
    return -4.0 * PlotRange.radius();
  }
  static max(){
    return 4.0 * PlotRange.radius();
  }
}
/**
 *
 */
function getPlotLayoutData() {
  return {
    xaxis: {
      range: [PlotRange.min(), PlotRange.max()],
      zeroline: false,
      visible: false,
    },
    yaxis: {
      scaleanchor: "x",
      range: [PlotRange.min(), PlotRange.max()],
      zeroline: false,
      visible: false,
    },

    autosize: true,
    margin: { l: 40, r: 40, b: 40, t: 40 },
    shapes: [
      // Main Circle
      {
        type: "circle",
        xref: "x",
        yref: "y",
        fillcolor: "rgba(128, 128, 128, 1)",
        x0: -PlotRange.radius(),
        y0: -PlotRange.radius(),
        x1: PlotRange.radius(),
        y1: PlotRange.radius(),
        line: {
          color: "rgba(0, 0, 0, 1)",
        },
      },
      {
        type: "circle",
        xref: "x",
        yref: "y",
        fillcolor: "rgba(0, 255, 60, 0.6)",
        x0: -zetaNumber(),
        y0: -zetaNumber(),
        x1: zetaNumber(),
        y1: zetaNumber(),
        line: {
          color: "rgba(0, 0, 0, 1)",
        },
      },
    ],
  };
}

function assembleDataForPlotlyFigure(data) {
    return [
      {
        type: "contour",
        visible: true,
        x: data[0],
        y: data[1],
        z: data[2],
        colorscale: [
          [0, "rgb(232,74, 39)"],
          [0.5, "rgb(255,255,255)"],
          [1, "rgb(5,86,165)"],
        ],
        showscale: false,
        ncontours: 30,
        contours: {
          coloring: "fill",
        },
      },
    ];
}


// placehold plot
/**
 *
 */
function placeholderPlot() {
  var size = 100,
  x = new Array(size),
  y = new Array(size),
  z = new Array(size);

  for (var i = 0; i < size; i++) {
    x[i] = y[i] = -2 * Math.PI + (4 * Math.PI * i) / size;
    z[i] = new Array(size);
    for (var j = 0; j < size; j++) {
      z[i][j] = 1.0;
    }
  }
  // for (var i = 0; i < size; i++) {
  //   for (var j = 0; j < size; j++) {
  //     var r2 = x[i] * x[i] + y[j] * y[j];
  //     z[i][j] =
  //       Math.sin(x[i]) * Math.cos(y[j]) * Math.sin(x[j]) * Math.cos(y[i]);
  //   }
  // }

  let data = [x, y, z];

  Plotly.newPlot(
    "plot_div",
    assembleDataForPlotlyFigure(data),
    getPlotLayoutData()
  );
}

/**
 *
 */
async function init() {
  initButton.classList.add("button--loading");

  //loadingIndicator.classList.add("mr-2", "progressAnimate");
  const loader = new ScriptLoader(
      "https://cdn.jsdelivr.net/pyodide/v0.19.0/full/pyodide.js"
  );
  await loader.load();
  pyodide = await loadPyodide(
      { indexURL: "https://cdn.jsdelivr.net/pyodide/v0.19.0/full/" }
  );
  await pyodide.loadPackage([
      "numpy",
      "scipy",
      "sympy"
  ]);

  console.log("Numpy is now available ");

  // init process
  simulateButton.removeAttribute("disabled");
  archetypeSelection.removeAttribute("disabled");
  initButton.classList.remove("button--loading");

 // simulatorPromise = generateSimulator();
}

/**
 * @param start
 * @param stop
 * @param num
 * @param endpoint
 */
function linspace(start, stop, num, endpoint = true) {
    const div = endpoint ? (num - 1) : num;
    const step = (stop - start) / div;

    return Float32Array.from({ length: num }, (_, i) => start + step * i);
}

function generateXY(n_samples){
    const x = linspace(PlotRange.min(), PlotRange.max(), n_samples);
    const y = linspace(PlotRange.min(), PlotRange.max(), n_samples);
    return [x, y];
}

/**
 * @param config
 * @param times
 */
function generateSimulator(config) {
    return fileFetchPromise.then(res => pyodide.runPython(res))
        .then(_ => pyodide.globals.get("simulator")(config));
}


async function runSimulator(config) {
  simulatorPromise = generateSimulator(config);

  // simulatorPromise.then(config)
  simulatorPromise.then(sim => {
      // sim = Sim(config);

      // any simulator specific configuration
      const n_samples = 81;
      xy = generateXY(n_samples);
      // console.log(typeof())
      const py_z = sim(xy);
      const z = py_z.toJs();
      py_z.destroy();

      data = [...xy, z];
      Plotly.newPlot(
        "plot_div",
        assembleDataForPlotlyFigure(data),
        getPlotLayoutData()
      );
      }); //.then(sim => {sim.destroy()});
  // streamingPlot(config["womerseley"], config["cauchy"]);
}

function buildConfig() {
  return {
    "womersley" : womersleyNumber(),
    "cauchy" : cauchyNumber(),
    "pinned_zone_radius" : zetaNumber()
  };
}

/**
 *
 */
function startSimulator() {
  const config = buildConfig();
  console.log("starting simulator");
  runSimulator(config);
}

/**
 *
 */
function restartSimulator() {
  startSimulator();
}

/* Utilities */
/**
 * @param value
 * @param precision
 */
function round(value, precision = 1) {
  const multiplier = Math.pow(10, precision || 0);

  return (Math.round(value * multiplier) / multiplier).toFixed(precision);
}

/**
 * @param slider_value
 */
function transform(slider_value) {
  // range from 1--100, so we multiply by 0.1 to get the actual value
  // return parseFloat(slider_value) * 0.1;
  return parseInt(slider_value) == 0 ? 0.1 : (parseFloat(slider_value)) * 0.1;
}

/**
 * @param start
 * @param stop
 * @param num
 * @param endpoint
 */

/**
 *
 */
function womersleyNumber() {
  return round(transform(womersleySlider.value));
}

/**
 *
 */
function cauchyNumber() {
  // from 0 - 10 in step of 1 with stpe of 1
  return round(parseFloat(cauchySlider.value) * 0.01, 2);
}

function zetaNumber(){
  // 1 - 5 with step of 1
  return round(parseFloat(zetaSlider.value) * 0.1);
}

// function deltaDCNumber() {
//   // TODO : Fill
//   return round(womersleyNumber() / cauchyNumber());
// }

/* Display */
/**
 *
 */
function showWomersleyNumber() {
  womersleyReadout.innerHTML = womersleyNumber();
}

/**
 *
 */
function showCauchyNumber() {
  cauchyReadout.innerHTML = cauchyNumber();
}

function showZeta(){
  zetaReadout.innerHTML = zetaNumber();
}

// function showDeltaDCNumber() {
//   deltaAReadout.innerHTML = deltaDCNumber();
// }

// select buttons and input field
const initButton = document.querySelector("#initButton");

const simulateButton = document.querySelector("#simulateButton");
const archetypeSelection = document.querySelector("#archetypeSelection");
//const animateCheckBox = document.querySelector("#enableAnimate");

// loader
//const loadingIndicator = document.querySelector("#loadingIndicator");

// sliders
const womersleySlider = document.querySelector("#womersleySlider");
const cauchySlider = document.querySelector("#cauchySlider");
const zetaSlider = document.querySelector("#zetaSlider");

// readouts
const womersleyReadout = document.querySelector("#womersleyReadout");
const cauchyReadout = document.querySelector("#cauchyReadout");
const zetaReadout = document.querySelector("#zetaReadout");
const deltaDCReadout = document.querySelector("#deltaDCReadout");

// add event listeners
initButton.addEventListener("click", init, { once: true });
simulateButton.addEventListener("click", startSimulator, { once: true });

function setDefaultSimulationParameters() {
  // set default here
  // choose case from the drop down menu
  const defaults = (() => {
    switch (archetypeSelection.value) {
      case "elastic":
        return ElasticDefaultParams;
      case "rigid":
        return RigidDefaultParams;
    }
  })();

  // sliders
  womersleySlider.value = defaults.defaultWomersley();
  cauchySlider.value = defaults.defaultCau();
  zetaSlider.value = defaults.defaultZeta();
}

/**
 *
 */
function addListeners() {
  /**
   * @param fn
   */
  function reset_and_(fn) {
    // return a closure
    return () => {
      fn();
      // showDeltaANumber();
      if (pyodide != null) {
        restartSimulator();
      }
    };
  }

  const slider_pairs = [
    [womersleySlider, reset_and_(showWomersleyNumber)],
    [cauchySlider, reset_and_(showCauchyNumber)],
    [zetaSlider, reset_and_(showZeta)],
  ];

  slider_pairs.forEach((p) => {
    // p[0].addEventListener("input", p[1]);
    p[0].addEventListener("change", p[1]);
  });

  const selection_pairs = [
    [archetypeSelection, reset_and_(setDefaultSimulationParameters)],
  ];

  selection_pairs.forEach((p) => {
    p[0].addEventListener("change", p[1]);
  });
}

function showParameterInfo() {
  showWomersleyNumber();
  showCauchyNumber();
  showZeta();
  // showDeltaANumber();
}

// perform the gist fetching
const fileFetchPromise = fetchFile("streaming_sandbox.py");
addListeners();

MathJax.Hub.Queue(["Typeset", MathJax.Hub]); // LaTex enabled
setDefaultSimulationParameters();
showParameterInfo();
placeholderPlot();

// globals
let pyodide;
// var reset = true;
let simulatorPromise;
// var i = 0;

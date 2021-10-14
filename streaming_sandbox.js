/* Initialization functions*/

class DefaultTypeA {
  static defaultW() {
    return 8;
  }
  static defaultCau() {
    return 13;
  }
}

class DefaultTypeB {
  static defaultW() {
    return 12;
  }
  static defaultCau() {
    return 49;
  }
}

/**
 *
 */
function getPlotLayoutData() {
  return {
    xaxis: {
      range: [-3, 3],
      zeroline: false,
      visible: false,
    },
    yaxis: {
      range: [-3, 3],
      zeroline: false,
      visible: false,
    },

    autosize: true,
    margin: { l: 40, r: 40, b: 40, t: 40 },
    shapes: [
      // Unfilled Circle

      {
        type: "circle",
        xref: "x",
        yref: "y",
        fillcolor: "rgba(128, 128, 128, 1)",
        x0: -1,
        y0: -1,
        x1: 1,
        y1: 1,
        line: {
          color: "rgba(0, 0, 0, 1)",
        },
      },
    ],
  };
}

// placehold plot
/**
 *
 */
function placeholderPlot() {
  var size = 100,
    x = new Array(size),
    y = new Array(size),
    z = new Array(size),
    i,
    j;
  for (var i = 0; i < size; i++) {
    x[i] = y[i] = -2 * Math.PI + (4 * Math.PI * i) / size;
    z[i] = new Array(size);
  }
  for (var i = 0; i < size; i++) {
    for (var j = 0; j < size; j++) {
      var r2 = x[i] * x[i] + y[j] * y[j];
      z[i][j] =
        Math.sin(x[i]) * Math.cos(y[j]) * Math.sin(x[j]) * Math.cos(y[i]);
    }
  }
  Plotly.newPlot(
    "plot_div",
    [
      {
        type: "contour",
        visible: true,
        x: x,
        y: y,
        z: z,
        colorscale: [
          [0, "rgb(232,74, 39)"],
          [0.5, "rgb(255,255,255)"],
          [1, "rgb(5,86,165)"],
        ],
        showscale: false,
        contours: {
          coloring: "fill",
        },
      },
    ],
    getPlotLayoutData()
  );
}

function changePlot(wn, cn) {
  var size = 100,
    x = new Array(size),
    y = new Array(size),
    z = new Array(size),
    i,
    j;
  for (var i = 0; i < size; i++) {
    x[i] = y[i] = -2 * Math.PI * wn + (4 * Math.PI * i) / size;
    z[i] = new Array(size);
  }
  for (var i = 0; i < size; i++) {
    for (var j = 0; j < size; j++) {
      var r2 = x[i] * x[i] + y[j] * y[j];
      z[i][j] =
        Math.sin(x[i]) * Math.cos(y[j]) * Math.sin(x[j]) * Math.cos(y[i]) * cn;
    }
  }
  Plotly.newPlot(
    "plot_div",
    [
      {
        type: "contour",
        visible: true,
        x: x,
        y: y,
        z: z,
        colorscale: [
          [0, "rgb(232,74, 39)"],
          [0.5, "rgb(255,255,255)"],
          [1, "rgb(5,86,165)"],
        ],
        showscale: false,
        contours: {
          coloring: "fill",
        },
      },
    ],
    getPlotLayoutData()
  );
}

/**
 *
 */
async function init() {
  initButton.classList.add("button--loading");
  // init process
  simulateButton.removeAttribute("disabled");
  archetypeSelection.removeAttribute("disabled");
  initButton.classList.remove("button--loading");
}

async function runSimulator() {
  changePlot(womersleyNumber(), cauchyNumber());
}

/**
 *
 */
function restartSimulator() {
  startSimulator();
}

/**
 *
 */
function startSimulator() {
  runSimulator();

  console.log("starting simulator");
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
  return parseFloat(slider_value) * 0.1;
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
  return round(transform(cauchySlider.value));
}

function deltaANumber() {
  return round(womersleyNumber() / cauchyNumber());
}

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

function showDeltaANumber() {
  deltaAReadout.innerHTML = deltaANumber();
}

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

// readouts
const womersleyReadout = document.querySelector("#womersleyReadout");
const cauchyReadout = document.querySelector("#cauchyReadout");
const deltaAReadout = document.querySelector("#deltaAReadout");

// add event listeners
initButton.addEventListener("click", init, { once: true });
simulateButton.addEventListener("click", runSimulator, { once: true });

function defaultSimulationParameters() {
  // set default here
  // choose case from the drop down menu
  const defaults = (() => {
    switch (archetypeSelection.value) {
      case "h1":
        return DefaultTypeA;
      case "h2":
        return DefaultTypeB;
    }
  })();

  // sliders
  womersleySlider.value = defaults.defaultW();
  cauchySlider.value = defaults.defaultCau();
  showParameterInfo();
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
      showDeltaANumber();
      restartSimulator();
    };
  }

  const slider_pairs = [
    [womersleySlider, reset_and_(showWomersleyNumber)],
    [cauchySlider, reset_and_(showCauchyNumber)],
  ];

  slider_pairs.forEach((p) => {
    p[0].addEventListener("input", p[1]);
    p[0].addEventListener("change", p[1]);
  });

  const selection_pairs = [
    [archetypeSelection, reset_and_(defaultSimulationParameters)],
  ];

  selection_pairs.forEach((p) => {
    p[0].addEventListener("change", p[1]);
  });
}

function showParameterInfo() {
  showWomersleyNumber();
  showCauchyNumber();
}

addListeners();

MathJax.Hub.Queue(["Typeset", MathJax.Hub]); // LaTex enabled
defaultSimulationParameters();
placeholderPlot();

// display at first go
showWomersleyNumber();
showCauchyNumber();
showDeltaANumber();

// globals
let requestID;
var reset = true;
let simulatorPromise;
var i = 0;

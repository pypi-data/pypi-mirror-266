"use strict";

exports.__esModule = true;
exports.HistogramVis = void 0;
var _react = _interopRequireWildcard(require("react"));
var d3 = _interopRequireWildcard(require("d3"));
function _getRequireWildcardCache(e) { if ("function" != typeof WeakMap) return null; var r = new WeakMap(), t = new WeakMap(); return (_getRequireWildcardCache = function _getRequireWildcardCache(e) { return e ? t : r; })(e); }
function _interopRequireWildcard(e, r) { if (!r && e && e.__esModule) return e; if (null === e || "object" != typeof e && "function" != typeof e) return { "default": e }; var t = _getRequireWildcardCache(r); if (t && t.has(e)) return t.get(e); var n = { __proto__: null }, a = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var u in e) if ("default" !== u && Object.prototype.hasOwnProperty.call(e, u)) { var i = a ? Object.getOwnPropertyDescriptor(e, u) : null; i && (i.get || i.set) ? Object.defineProperty(n, u, i) : n[u] = e[u]; } return n["default"] = e, t && t.set(e, n), n; }
function _createForOfIteratorHelperLoose(o, allowArrayLike) { var it = typeof Symbol !== "undefined" && o[Symbol.iterator] || o["@@iterator"]; if (it) return (it = it.call(o)).next.bind(it); if (Array.isArray(o) || (it = _unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") { if (it) o = it; var i = 0; return function () { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }
function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) arr2[i] = arr[i]; return arr2; }
var HistogramVis = exports.HistogramVis = function HistogramVis(_ref) {
  var _ref$data = _ref.data,
    data = _ref$data === void 0 ? [] : _ref$data,
    _ref$dataTypes = _ref.dataTypes,
    dataTypes = _ref$dataTypes === void 0 ? {} : _ref$dataTypes,
    _ref$variable = _ref.variable,
    variable = _ref$variable === void 0 ? "" : _ref$variable,
    _ref$layout = _ref.layout,
    layout = _ref$layout === void 0 ? {
      "height": 80,
      "width": 210,
      "marginRight": 15,
      "marginLeft": 5,
      "marginTop": 5,
      "marginBottom": 20
    } : _ref$layout,
    currentFilters = _ref.currentFilters,
    handleFilter = _ref.handleFilter;
  var ref = (0, _react.useRef)("svgCompare");
  function getTickValues(values) {
    if (values.length < 10) {
      return values;
    } else {
      var tickScale = d3.scaleLinear().domain(d3.extent(values)).range([layout.marginLeft, layout.width - layout.marginRight]);
      var tickAxis = d3.axisBottom(tickScale).ticks(5);
      return tickAxis.scale().ticks();
    }
  }
  (0, _react.useEffect)(function () {
    var svg = d3.select(ref.current);
    var svgElement = svg.select("#vis");
    var type = dataTypes[variable].type;
    if (type === "string") {
      var bins = d3.bin().thresholds(10).value(function (d) {
        return d.length;
      })(data.map(function (d) {
        return d[variable];
      }));

      // Declare the x (horizontal position) scale.
      var x = d3.scaleLinear().domain([bins[0].x0, bins[bins.length - 1].x1]).range([layout.marginLeft, layout.width - layout.marginRight]);

      // Declare the y (vertical position) scale.
      var y = d3.scaleLinear().domain([0, d3.max(bins, function (d) {
        return d.length;
      })]).range([layout.height - layout.marginBottom, layout.marginTop]);

      // Add a rect for each bin.
      svgElement.selectAll(".bins").data(bins).join("rect").attr("class", "bins").attr("x", function (d) {
        return bins.length > 1 ? x(d.x0) + 1 : layout.marginLeft + 1;
      }).attr("width", function (d) {
        return bins.length > 1 ? x(d.x1) - x(d.x0) - 1 : layout.width - layout.marginLeft - layout.marginRight - 2;
      }).attr("y", function (d) {
        return y(d.length);
      }).attr("height", function (d) {
        return y(0) - y(d.length);
      }).attr("cursor", "pointer").attr("fill", function (d) {
        if (!currentFilters || !currentFilters[variable]) {
          return "steelblue";
        }
        var filterValues = currentFilters[variable];
        if (filterValues.filter(function (a) {
          return a[0] <= x.invert(d.x0) && a[1] >= x.invert(d.x1);
        }).length == 0) {
          return "gray";
        } else {
          return "steelblue";
        }
      }).on("click", function (e, d) {
        if (bins.length === 1) {
          // Cannot filter if the entire data set is the same
          return;
        } else {
          var binMin = x.invert(d.x0);
          var binMax = x.invert(d.x1);
          handleFilter(variable, [binMin, binMax], currentFilters);
        }
      });

      // Add the x-axis and label.
      svg.select("#xaxis").attr("transform", "translate(0," + (layout.height - layout.marginBottom) + ")").call(d3.axisBottom(x).ticks(5).tickSizeOuter(0).tickSize(2)).call(function (g) {
        return g.select(".domain").remove();
      });
    } else if (type === "list") {
      var flatten = data.map(function (d) {
        return d[variable];
      }).flat();
      var counts = [];
      var _loop = function _loop() {
        var n = _step.value;
        var nCounts = flatten.filter(function (d) {
          return d === n;
        }).length;
        counts.push({
          "nVar": n,
          "nCounts": nCounts
        });
      };
      for (var _iterator = _createForOfIteratorHelperLoose(dataTypes[variable].ints), _step; !(_step = _iterator()).done;) {
        _loop();
      }

      // Declare the x (horizontal position) scale.
      var _x = d3.scaleBand().domain(counts.map(function (c) {
        return c.nVar;
      })).range([layout.marginLeft, layout.width - layout.marginRight]);

      // Declare the y (vertical position) scale.
      var _y = d3.scaleLinear().domain([0, d3.max(counts.map(function (c) {
        return c.nCounts;
      }))]).range([layout.height - layout.marginBottom, layout.marginTop]);

      // Add a rect for each bin.
      svgElement.selectAll(".bins").data(counts).join("rect").attr("class", "bins").attr("x", function (d) {
        return _x(d.nVar) + 1;
      }).attr("width", function (d) {
        return _x.bandwidth() - 2;
      }).attr("y", function (d) {
        return _y(d.nCounts);
      }).attr("height", function (d) {
        return _y(0) - _y(d.nCounts);
      }).attr("cursor", "pointer").attr("fill", function (d) {
        if (!currentFilters || !currentFilters[variable]) {
          return "steelblue";
        }
        var filterValues = currentFilters[variable];
        if (filterValues.filter(function (a) {
          return a == d.nVar;
        }).length == 0) {
          return "gray";
        } else {
          return "steelblue";
        }
      }).on("click", function (e, d) {
        handleFilter(variable, d.nVar, currentFilters);
      });

      // Add the x-axis and label.
      svg.select("#xaxis").attr("transform", "translate(0," + (layout.height - layout.marginBottom) + ")").call(d3.axisBottom(_x).tickValues(getTickValues(flatten)).tickSizeOuter(0).tickSize(2)).call(function (g) {
        return g.select(".domain").remove();
      });
    } else {
      var _counts = [];
      var _loop2 = function _loop2() {
        var n = _step2.value;
        var nCounts = data.filter(function (d) {
          return d[variable] === n;
        }).length;
        _counts.push({
          "nVar": n,
          "nCounts": nCounts
        });
      };
      for (var _iterator2 = _createForOfIteratorHelperLoose(dataTypes[variable].ints), _step2; !(_step2 = _iterator2()).done;) {
        _loop2();
      }

      // Declare the x (horizontal position) scale.
      var _x2 = d3.scaleBand().domain(_counts.map(function (c) {
        return c.nVar;
      })).range([layout.marginLeft, layout.width - layout.marginRight]);

      // Declare the y (vertical position) scale.
      var _y2 = d3.scaleLinear().domain([0, d3.max(_counts.map(function (c) {
        return c.nCounts;
      }))]).range([layout.height - layout.marginBottom, layout.marginTop]);

      // Add a rect for each bin.
      svgElement.selectAll(".bins").data(_counts).join("rect").attr("class", "bins").attr("x", function (d) {
        return _x2(d.nVar) + 1;
      }).attr("width", function (d) {
        return _x2.bandwidth() - 2;
      }).attr("y", function (d) {
        return _y2(d.nCounts);
      }).attr("height", function (d) {
        return _y2(0) - _y2(d.nCounts);
      }).attr("cursor", "pointer").attr("fill", function (d) {
        if (!currentFilters || !currentFilters[variable]) {
          return "steelblue";
        }
        var filterValues = currentFilters[variable];
        if (filterValues.filter(function (a) {
          return a == d.nVar;
        }).length == 0) {
          return "gray";
        } else {
          return "steelblue";
        }
      }).on("click", function (e, d) {
        handleFilter(variable, d.nVar, currentFilters);
      });

      // Add the x-axis and label.
      svg.select("#xaxis").attr("transform", "translate(0," + (layout.height - layout.marginBottom) + ")").call(d3.axisBottom(_x2).ticks(5).tickSizeOuter(0).tickSize(2)).call(function (g) {
        return g.select(".domain").remove();
      });
    }
  }, [data, dataTypes, variable, currentFilters]);
  return /*#__PURE__*/_react["default"].createElement("div", null, /*#__PURE__*/_react["default"].createElement("svg", {
    width: layout.width,
    height: layout.height,
    ref: ref
  }, /*#__PURE__*/_react["default"].createElement("g", {
    id: "vis"
  }), /*#__PURE__*/_react["default"].createElement("g", {
    id: "xaxis"
  })));
};
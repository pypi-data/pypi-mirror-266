"use strict";

exports.__esModule = true;
exports.UMAPVis = void 0;
var _react = _interopRequireWildcard(require("react"));
var d3 = _interopRequireWildcard(require("d3"));
var _Button = _interopRequireDefault(require("@mui/material/Button"));
var _SelectedTable = require("./SelectedTable.js");
var _Search = require("./Search.js");
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }
function _getRequireWildcardCache(e) { if ("function" != typeof WeakMap) return null; var r = new WeakMap(), t = new WeakMap(); return (_getRequireWildcardCache = function _getRequireWildcardCache(e) { return e ? t : r; })(e); }
function _interopRequireWildcard(e, r) { if (!r && e && e.__esModule) return e; if (null === e || "object" != typeof e && "function" != typeof e) return { "default": e }; var t = _getRequireWildcardCache(r); if (t && t.has(e)) return t.get(e); var n = { __proto__: null }, a = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var u in e) if ("default" !== u && Object.prototype.hasOwnProperty.call(e, u)) { var i = a ? Object.getOwnPropertyDescriptor(e, u) : null; i && (i.get || i.set) ? Object.defineProperty(n, u, i) : n[u] = e[u]; } return n["default"] = e, t && t.set(e, n), n; }
var UMAPVis = exports.UMAPVis = function UMAPVis(_ref) {
  var _ref$allTrainData = _ref.allTrainData,
    allTrainData = _ref$allTrainData === void 0 ? [] : _ref$allTrainData,
    _ref$allTestData = _ref.allTestData,
    allTestData = _ref$allTestData === void 0 ? [] : _ref$allTestData,
    _ref$layout = _ref.layout,
    layout = _ref$layout === void 0 ? {
      "height": 500,
      "width": 650,
      "marginRight": 25,
      "marginLeft": 25,
      "marginTop": 25,
      "marginBottom": 25
    } : _ref$layout,
    _queryInput = _ref._queryInput;
  var ref = (0, _react.useRef)("svgUMAP");
  var _useState = (0, _react.useState)([]),
    brushed = _useState[0],
    setBrushed = _useState[1];
  var _useState2 = (0, _react.useState)(""),
    searchStr = _useState2[0],
    setSearchStr = _useState2[1];
  var _useState3 = (0, _react.useState)(null),
    hover = _useState3[0],
    setHover = _useState3[1];
  (0, _react.useEffect)(function () {
    var svg = d3.select(ref.current);
    var svgElement = svg.select("#vis");
    var xExtent = d3.extent(allTrainData.concat(allTestData), function (d) {
      return d["0"];
    });
    var yExtent = d3.extent(allTrainData.concat(allTestData), function (d) {
      return d["1"];
    });

    // Declare the x (horizontal position) scale.
    var x = d3.scaleLinear().domain(xExtent).range([layout.marginLeft, layout.width - layout.marginRight]);

    // Declare the y (vertical position) scale.
    var y = d3.scaleLinear().domain(yExtent).range([layout.height - layout.marginBottom, layout.marginTop]);
    var uniqueLabels = Array.from(new Set(allTrainData.map(function (d) {
      return d.label;
    })));
    var colorScale = d3.scaleOrdinal(d3.schemeSet2).domain(uniqueLabels);

    // Add a rect for each bin.
    var trainDataPoint = svgElement.select("#train").selectAll(".trainEmbeddings").data(allTrainData).join("circle").attr("class", "trainEmbeddings").attr("cx", function (d) {
      return x(d["0"]);
    }).attr("cy", function (d) {
      return y(d["1"]);
    }).attr("r", 3).attr("fill", "none").attr("stroke", function (d, i) {
      return colorScale(d.label);
    }).attr("opacity", 0.25);

    // Add a rect for each bin.
    var testDataPoint = svgElement.select("#test").selectAll(".testEmbeddings").data(allTestData).join("circle").attr("class", "testEmbeddings").attr("cx", function (d) {
      return x(d["0"]);
    }).attr("cy", function (d) {
      return y(d["1"]);
    }).attr("r", 3).attr("fill", "red").on("mouseover", function (d, i) {
      setHover(i);
    }).on("mouseout", setHover(null));
    var brush = d3.brush().on("start brush end", function (_ref2) {
      var selection = _ref2.selection;
      var value = [];
      if (selection) {
        d3.select(".selection").attr("fill", "none").attr("stroke", "gray").attr("stroke-dasharray", "2px 5px 5px 5px");
        var _selection$ = selection[0],
          x0 = _selection$[0],
          y0 = _selection$[1],
          _selection$2 = selection[1],
          x1 = _selection$2[0],
          y1 = _selection$2[1];
        trainDataPoint.attr("fill", function (d, i) {
          if (x0 <= x(d["0"]) && x(d["0"]) < x1 && y0 <= y(d["1"]) && y(d["1"]) < y1) {
            return colorScale(d.label);
          } else {
            return "none";
          }
        }).attr("stroke", function (d, i) {
          if (x0 <= x(d["0"]) && x(d["0"]) < x1 && y0 <= y(d["1"]) && y(d["1"]) < y1) {
            return colorScale(d.label);
          } else {
            return "gray";
          }
        }).attr("opacity", function (d, i) {
          if (x0 <= x(d["0"]) && x(d["0"]) < x1 && y0 <= y(d["1"]) && y(d["1"]) < y1) {
            return 0.5;
          } else {
            return 0.25;
          }
        });
        value = allTrainData.filter(function (d, i) {
          return x0 <= x(d["0"]) && x(d["0"]) < x1 && y0 <= y(d["1"]) && y(d["1"]) < y1;
        });
        setBrushed(value);
      } else {
        trainDataPoint.attr("stroke", function (d, i) {
          return colorScale(d.label);
        }).attr("fill", "none").attr("opacity", 0.25);
      }
    });

    // Create the brush behavior.
    svg.call(brush);
  }, [allTrainData, allTestData]);
  function runQuery(query) {
    if (query) {
      var hidden = document.getElementById(_queryInput);
      var data_string = JSON.stringify([query]);
      if (hidden) {
        hidden.value = data_string;
        var event = document.createEvent('HTMLEvents');
        event.initEvent('input', false, true);
        hidden.dispatchEvent(event);
      }
    }
  }
  return /*#__PURE__*/_react["default"].createElement("div", null, /*#__PURE__*/_react["default"].createElement("p", null, "Brush to select training sentences for comparison."), /*#__PURE__*/_react["default"].createElement("svg", {
    width: layout.width,
    height: layout.height,
    ref: ref
  }, /*#__PURE__*/_react["default"].createElement("g", {
    id: "vis"
  }, /*#__PURE__*/_react["default"].createElement("g", {
    id: "train"
  }), /*#__PURE__*/_react["default"].createElement("g", {
    id: "test"
  })), /*#__PURE__*/_react["default"].createElement("g", {
    id: "xaxis"
  })), /*#__PURE__*/_react["default"].createElement("div", {
    style: {
      "display": "flex",
      "alignItems": "center"
    }
  }, /*#__PURE__*/_react["default"].createElement(_Search.Search, {
    title: "Query Sentence",
    width: 550 - 25 + "px",
    setSearchStr: setSearchStr
  }), /*#__PURE__*/_react["default"].createElement(_Button["default"], {
    style: {
      "height": "40px"
    },
    variant: "outlined",
    onClick: function onClick(event) {
      runQuery(searchStr);
    }
  }, "Compute")), /*#__PURE__*/_react["default"].createElement(_SelectedTable.SelectedTable, {
    selectedData: allTestData,
    hover: hover
  }), /*#__PURE__*/_react["default"].createElement(_SelectedTable.SelectedTable, {
    title: "Compare",
    selectedData: brushed
  }));
};
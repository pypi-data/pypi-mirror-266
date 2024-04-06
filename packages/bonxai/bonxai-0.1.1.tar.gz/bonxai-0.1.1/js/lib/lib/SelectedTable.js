"use strict";

exports.__esModule = true;
exports.SelectedTable = void 0;
var React = _interopRequireWildcard(require("react"));
var _Table = _interopRequireDefault(require("@mui/material/Table"));
var _TableBody = _interopRequireDefault(require("@mui/material/TableBody"));
var _TableCell = _interopRequireDefault(require("@mui/material/TableCell"));
var _TableContainer = _interopRequireDefault(require("@mui/material/TableContainer"));
var _TableHead = _interopRequireDefault(require("@mui/material/TableHead"));
var _TableRow = _interopRequireDefault(require("@mui/material/TableRow"));
var _Paper = _interopRequireDefault(require("@mui/material/Paper"));
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }
function _getRequireWildcardCache(e) { if ("function" != typeof WeakMap) return null; var r = new WeakMap(), t = new WeakMap(); return (_getRequireWildcardCache = function _getRequireWildcardCache(e) { return e ? t : r; })(e); }
function _interopRequireWildcard(e, r) { if (!r && e && e.__esModule) return e; if (null === e || "object" != typeof e && "function" != typeof e) return { "default": e }; var t = _getRequireWildcardCache(r); if (t && t.has(e)) return t.get(e); var n = { __proto__: null }, a = Object.defineProperty && Object.getOwnPropertyDescriptor; for (var u in e) if ("default" !== u && Object.prototype.hasOwnProperty.call(e, u)) { var i = a ? Object.getOwnPropertyDescriptor(e, u) : null; i && (i.get || i.set) ? Object.defineProperty(n, u, i) : n[u] = e[u]; } return n["default"] = e, t && t.set(e, n), n; }
var SelectedTable = exports.SelectedTable = function SelectedTable(_ref) {
  var _ref$title = _ref.title,
    title = _ref$title === void 0 ? "Queries" : _ref$title,
    _ref$selectedData = _ref.selectedData,
    selectedData = _ref$selectedData === void 0 ? [] : _ref$selectedData,
    _ref$testData = _ref.testData,
    testData = _ref$testData === void 0 ? [] : _ref$testData,
    _ref$testDataPredicti = _ref.testDataPrediction,
    testDataPrediction = _ref$testDataPredicti === void 0 ? [] : _ref$testDataPredicti,
    hover = _ref.hover;
  return /*#__PURE__*/React.createElement("div", {
    style: {
      "marginTop": "50px"
    }
  }, /*#__PURE__*/React.createElement("p", null, title), /*#__PURE__*/React.createElement(_TableContainer["default"], {
    component: _Paper["default"],
    sx: {
      "width": "650px"
    },
    style: {
      maxHeight: 500
    }
  }, /*#__PURE__*/React.createElement(_Table["default"], {
    sx: {
      maxWidth: 650
    },
    size: "small",
    "aria-label": "a dense table",
    stickyHeader: true
  }, /*#__PURE__*/React.createElement(_TableHead["default"], null, /*#__PURE__*/React.createElement(_TableRow["default"], null, /*#__PURE__*/React.createElement(_TableCell["default"], null, "text"), /*#__PURE__*/React.createElement(_TableCell["default"], null, "label"))), /*#__PURE__*/React.createElement(_TableBody["default"], {
    style: {
      "maxHeight": "200px",
      "overflow": "scroll"
    }
  }, selectedData.map(function (row, i) {
    return /*#__PURE__*/React.createElement(_TableRow["default"], {
      key: "row" + i,
      sx: {
        backgroundColor: i == hover ? "#efefef" : "none",
        '&:last-child td, &:last-child th': {
          border: 0
        }
      }
    }, /*#__PURE__*/React.createElement(_TableCell["default"], {
      component: "th",
      scope: "row"
    }, row.text), /*#__PURE__*/React.createElement(_TableCell["default"], null, row.label));
  })))));
};